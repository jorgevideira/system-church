from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_admin
from app.db.models.payment_account import PaymentAccount
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.payment_account import (
    PaymentAccountCreate,
    PaymentAccountOAuthStartResponse,
    PaymentAccountResponse,
    PaymentAccountUpdate,
)
from app.services import mercadopago_oauth_service, payment_account_service, secret_service

router = APIRouter()


@router.get("/", response_model=List[PaymentAccountResponse])
def list_payment_accounts(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[PaymentAccountResponse]:
    return payment_account_service.list_payment_account_responses(db, current_tenant.id)


@router.post("/", response_model=PaymentAccountResponse, status_code=status.HTTP_201_CREATED)
def create_payment_account(
    payload: PaymentAccountCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaymentAccountResponse:
    try:
        account = payment_account_service.create_payment_account(db, current_tenant.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return payment_account_service.to_response(account)


@router.put("/{account_id}", response_model=PaymentAccountResponse)
def update_payment_account(
    account_id: int,
    payload: PaymentAccountUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaymentAccountResponse:
    account = payment_account_service.get_payment_account(db, account_id, current_tenant.id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment account not found")
    try:
        updated = payment_account_service.update_payment_account(db, account, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return payment_account_service.to_response(updated)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_account(
    account_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    account = payment_account_service.get_payment_account(db, account_id, current_tenant.id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment account not found")
    payment_account_service.delete_payment_account(db, account)


@router.post("/{account_id}/oauth/mercadopago/start", response_model=PaymentAccountOAuthStartResponse)
def start_mercadopago_oauth(
    account_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaymentAccountOAuthStartResponse:
    account = payment_account_service.get_payment_account(db, account_id, current_tenant.id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment account not found")
    if account.provider != "mercadopago":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth is only available for Mercado Pago accounts")
    try:
        state = mercadopago_oauth_service.generate_state()
        payment_account_service.update_oauth_metadata(db, account, connected=False, last_error=None, state=state)
        return PaymentAccountOAuthStartResponse(authorize_url=mercadopago_oauth_service.build_authorize_url(state))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/oauth/mercadopago/callback", response_class=HTMLResponse, include_in_schema=False)
def mercadopago_oauth_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    def render(status_text: str, description: str) -> HTMLResponse:
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Conexão Mercado Pago</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#f4f8fc; color:#16324a; display:flex; align-items:center; justify-content:center; min-height:100vh; margin:0; }}
    .card {{ background:#fff; border-radius:18px; padding:24px; box-shadow:0 18px 40px rgba(22,50,74,.12); width:min(520px,92vw); }}
    h1 {{ margin:0 0 10px; font-size:24px; }}
    p {{ margin:0 0 10px; line-height:1.5; }}
    button {{ margin-top:12px; border:0; border-radius:999px; padding:10px 16px; background:#0f7ccf; color:#fff; cursor:pointer; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{status_text}</h1>
    <p>{description}</p>
    <button onclick="window.close()">Fechar</button>
  </div>
  <script>
    if (window.opener) {{
      window.opener.postMessage({{ type: "mercadopago-oauth", status: "{status_text}" }}, "*");
    }}
  </script>
</body>
</html>
"""
        return HTMLResponse(content=html)

    if not state:
        return render("Falha na conexão", "O retorno do Mercado Pago veio sem estado de segurança.")

    account = (
        db.query(PaymentAccount)
        .filter(PaymentAccount.provider == "mercadopago")
        .all()
    )
    matched_account = None
    for candidate in account:
        config = candidate.config_json or {}
        if str(config.get("oauth_state") or "") == state:
            matched_account = candidate
            break
    if matched_account is None:
        return render("Falha na conexão", "Não foi possível localizar a conta de pagamento que iniciou a autorização.")

    if error:
        payment_account_service.update_oauth_metadata(
            db,
            matched_account,
            connected=False,
            last_error=(error_description or error),
            state=None,
        )
        return render("Conexão cancelada", error_description or error)

    if not code:
        payment_account_service.update_oauth_metadata(db, matched_account, connected=False, last_error="Authorization code missing", state=None)
        return render("Falha na conexão", "O Mercado Pago não retornou o código de autorização.")

    try:
        token_payload = mercadopago_oauth_service.exchange_code(code)
        access_token = token_payload.get("access_token")
        refresh_token = token_payload.get("refresh_token")
        user_id = token_payload.get("user_id")
        public_key = token_payload.get("public_key")
        matched_account.secrets_json = dict(matched_account.secrets_json or {})
        matched_account.secrets_json["access_token"] = secret_service.encrypt_value(access_token)
        payment_account_service.update_oauth_metadata(
            db,
            matched_account,
            connected=True,
            provider_user_id=str(user_id) if user_id is not None else None,
            refresh_token=str(refresh_token) if refresh_token is not None else None,
            public_key=str(public_key) if public_key else None,
            last_error=None,
            state=None,
        )
        return render("Conta conectada", "A conta do Mercado Pago foi conectada com sucesso e já pode ser usada nos eventos.")
    except Exception as exc:
        payment_account_service.update_oauth_metadata(
            db,
            matched_account,
            connected=False,
            last_error=str(exc),
            state=None,
        )
        return render("Falha na conexão", "A autorização retornou, mas a troca do código por token não foi concluída.")
