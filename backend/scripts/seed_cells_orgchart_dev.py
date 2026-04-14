#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import random
import string
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import time
from typing import Any

import requests


WEEKDAYS = [
    ("monday", 0),
    ("tuesday", 1),
    ("wednesday", 2),
    ("thursday", 3),
    ("friday", 4),
    ("saturday", 5),
    ("sunday", 6),
]


BIBLICAL_NAMES = [
    "Abraao", "Sara", "Isaque", "Rebeca", "Jaco", "Raquel", "Jose", "Moises", "Miriam", "Josue",
    "Calebe", "Debora", "Gideao", "Rute", "Samuel", "Davi", "Salomao", "Elias", "Eliseu", "Ester",
    "Daniel", "Neemias", "Esdras", "Jó", "Isaías", "Jeremias", "Ezequiel", "Oseias", "Jonas", "Miqueias",
    "Zacarias", "Joao Batista", "Maria", "Jose (pai de Jesus)", "Pedro", "Tiago", "Joao", "Andre",
    "Filipe", "Bartolomeu", "Mateus", "Tome", "Simão", "Judas (Tadeu)", "Paulo", "Barnabe", "Timoteo",
    "Tito", "Lidia", "Priscila", "Aquila",
]


CELL_THEMES = [
    "Oração e Comunhão",
    "Fé que Move Montanhas",
    "Discípulos e Missão",
    "Graça e Verdade",
    "Família no Altar",
    "Servindo com Alegria",
]


def _is_dev_url(url: str) -> bool:
    lowered = url.strip().lower()
    if "prod" in lowered:
        return False
    if lowered.startswith("http://localhost") or lowered.startswith("http://127.0.0.1"):
        return True
    return "dev" in lowered


def _rand_suffix(n: int = 6) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(n))


def _slugify_email(name: str) -> str:
    base = "".join(ch for ch in name.lower() if ch.isalnum() or ch in {"_", "."}).strip(".")
    base = base.replace(" ", ".")
    base = base.replace("__", "_")
    return base or f"user.{_rand_suffix(4)}"


def _pick_unique_names(count: int, *, prefix: str) -> list[str]:
    pool = list(BIBLICAL_NAMES)
    random.shuffle(pool)
    result = []
    for i in range(count):
        base = pool[i % len(pool)]
        # Keep names unique even if we wrap the pool.
        result.append(f"{base} ({prefix} {i + 1:02d})")
    return result


def _month_date_range(year: int, month: int) -> tuple[date, date]:
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return date(year, month, 1), end


def _iter_weekday_dates(start: date, end: date, weekday: int) -> list[date]:
    cur = start
    # move to next weekday
    while cur.weekday() != weekday:
        cur += timedelta(days=1)
    out = []
    while cur <= end:
        out.append(cur)
        cur += timedelta(days=7)
    return out


@dataclass
class ApiClient:
    base_url: str
    token: str
    admin_email: str | None = None
    admin_password: str | None = None

    def _url(self, path: str) -> str:
        return self.base_url.rstrip("/") + path

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
    ) -> requests.Response:
        reauthed = False
        last_exc: Exception | None = None
        for attempt in range(1, 6):
            try:
                resp = requests.request(
                    method,
                    self._url(path),
                    headers=self._headers(),
                    params=params,
                    json=json,
                    data=data,
                    timeout=90,
                )
                # Token may expire mid-seed; re-login once and retry.
                if resp.status_code == 401 and not reauthed and self.admin_email and self.admin_password:
                    self.token = login(self.base_url, self.admin_email, self.admin_password)
                    reauthed = True
                    continue
                # Retry on transient gateway / server errors.
                if resp.status_code in (502, 503, 504) or resp.status_code >= 500:
                    if attempt < 5:
                        time.sleep(0.6 * attempt)
                        continue
                return resp
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_exc = exc
                if attempt < 5:
                    time.sleep(0.6 * attempt)
                    continue
                raise
        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected request retry failure")

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        resp = self._request("GET", path, params=params)
        if not resp.ok:
            raise RuntimeError(f"GET {path} -> {resp.status_code}: {resp.text}")
        return resp.json()

    def post(self, path: str, *, json: Any | None = None, data: dict[str, Any] | None = None) -> Any:
        resp = self._request("POST", path, json=json, data=data)
        if not resp.ok:
            raise RuntimeError(f"POST {path} -> {resp.status_code}: {resp.text}")
        return resp.json() if resp.text else None

    def patch(self, path: str, *, json: Any | None = None) -> Any:
        resp = self._request("PATCH", path, json=json)
        if not resp.ok:
            raise RuntimeError(f"PATCH {path} -> {resp.status_code}: {resp.text}")
        return resp.json() if resp.text else None

    def delete(self, path: str) -> None:
        resp = self._request("DELETE", path)
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"DELETE {path} -> {resp.status_code}: {resp.text}")


def login(base_url: str, email: str, password: str) -> str:
    url = base_url.rstrip("/") + "/api/v1/auth/login"
    resp = requests.post(url, data={"username": email, "password": password}, timeout=60)
    if not resp.ok:
        raise RuntimeError(f"Login failed: {resp.status_code} {resp.text}")
    payload = resp.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError("Login did not return access_token")
    return token


def _get_or_create_user(api: ApiClient, *, email: str, full_name: str, role_id: int, password: str) -> dict:
    # Try find by listing (tenant scoped, paginated)
    skip = 0
    limit = 200
    while True:
        existing = api.get("/api/v1/users/", params={"skip": skip, "limit": limit})
        if not existing:
            break
        for u in existing:
            if (u.get("email") or "").lower() == email.lower():
                return u
        if len(existing) < limit:
            break
        skip += limit

    return api.post(
        "/api/v1/users/",
        json={
            "email": email,
            "full_name": full_name,
            "role": "viewer",
            "role_id": role_id,
            "password": password,
        },
    )


def _get_or_create_member_for_user(api: ApiClient, *, user: dict, count_start_date: str) -> dict:
    members = api.get("/api/v1/cells/members/all", params={"status": "active"})
    for m in members:
        if int(m.get("user_id") or 0) == int(user["id"]):
            return m

    full_name = user.get("full_name") or user.get("email") or f"Usuario {user['id']}"
    return api.post(
        "/api/v1/cells/members/all",
        json={
            "full_name": full_name,
            "contact": None,
            "status": "active",
            "user_id": user["id"],
            "stage": "member",
            "count_start_date": count_start_date,
        },
    )


def _create_member(api: ApiClient, *, full_name: str, stage: str, count_start_date: str) -> dict:
    return api.post(
        "/api/v1/cells/members/all",
        json={
            "full_name": full_name,
            "contact": None,
            "status": "active",
            "stage": stage,
            "count_start_date": count_start_date,
        },
    )


def _get_or_create_cell(api: ApiClient, *, name: str, weekday: str, meeting_time: str, address: str) -> dict:
    cells = api.get("/api/v1/cells/", params={"status": None})
    for c in cells:
        if (c.get("name") or "").strip().lower() == name.strip().lower():
            return c

    return api.post(
        "/api/v1/cells/",
        json={
            "name": name,
            "weekday": weekday,
            "meeting_time": meeting_time,
            "address": address,
            "status": "active",
        },
    )


def _ensure_member_link(api: ApiClient, *, cell_id: int, member_id: int) -> None:
    # Attempt create; if already exists API returns 400/409 depending on service behavior.
    try:
        api.post(f"/api/v1/cells/{cell_id}/members/{member_id}", json={})
    except RuntimeError as exc:
        msg = str(exc)
        if "400" in msg or "409" in msg:
            return
        raise


def _assign_leadership(api: ApiClient, *, cell_id: int, member_id: int, role: str, discipler_member_id: int | None) -> dict:
    payload: dict[str, Any] = {"member_id": member_id, "role": role, "is_primary": role == "leader"}
    if discipler_member_id is not None:
        payload["discipler_member_id"] = discipler_member_id
    return api.post(f"/api/v1/cells/{cell_id}/leaders", json=payload)


def _sync_cell_leadership(
    api: ApiClient,
    *,
    cell_id: int,
    discipler_member_id: int,
    leader_member_id: int,
    network_pastor_member_id: int | None,
) -> None:
    assignments = api.get(f"/api/v1/cells/{cell_id}/leaders")
    rows = assignments if isinstance(assignments, list) else []

    desired_pastor_id = network_pastor_member_id or None

    active_rows = [r for r in rows if r and r.get("active")]
    for r in active_rows:
        role = r.get("role")
        if role not in ("co_leader", "leader"):
            continue
        keep = False
        if role == "co_leader":
            keep = int(r.get("member_id") or 0) == discipler_member_id and (r.get("discipler_member_id") or None) == desired_pastor_id
        if role == "leader":
            keep = int(r.get("member_id") or 0) == leader_member_id and int(r.get("discipler_member_id") or 0) == discipler_member_id
        if keep:
            continue
        api.patch(f"/api/v1/cells/{cell_id}/leaders/{int(r['id'])}", json={"active": False})

    # Refresh
    rows = api.get(f"/api/v1/cells/{cell_id}/leaders")
    rows = rows if isinstance(rows, list) else []
    has_co = any(
        r and r.get("active") and r.get("role") == "co_leader"
        and int(r.get("member_id") or 0) == discipler_member_id
        and (r.get("discipler_member_id") or None) == desired_pastor_id
        for r in rows
    )
    if not has_co:
        _assign_leadership(api, cell_id=cell_id, member_id=discipler_member_id, role="co_leader", discipler_member_id=desired_pastor_id)

    has_leader = any(
        r and r.get("active") and r.get("role") == "leader"
        and int(r.get("member_id") or 0) == leader_member_id
        and int(r.get("discipler_member_id") or 0) == discipler_member_id
        for r in rows
    )
    if not has_leader:
        _assign_leadership(api, cell_id=cell_id, member_id=leader_member_id, role="leader", discipler_member_id=discipler_member_id)


def _list_meetings(api: ApiClient, *, cell_id: int, start: date, end: date) -> list[dict]:
    return api.get(
        f"/api/v1/cells/{cell_id}/meetings",
        params={"start_date": start.isoformat(), "end_date": end.isoformat()},
    )


def _upsert_attendance(api: ApiClient, *, meeting_id: int, items: list[dict]) -> None:
    path = f"/api/v1/cells/meetings/{meeting_id}/attendances/bulk"
    try:
        api.post(path, json={"items": items})
        return
    except RuntimeError as exc:
        msg = str(exc)
        # Some environments may intermittently 500 on big payloads; fall back to smaller chunks.
        if "-> 500" not in msg:
            raise

    def chunks(seq: list[dict], size: int):
        for i in range(0, len(seq), size):
            yield seq[i : i + size]

    for size in (20, 10, 5, 1):
        try:
            for part in chunks(items, size):
                api.post(path, json={"items": part})
            return
        except RuntimeError:
            continue
    raise


def seed(args: argparse.Namespace) -> None:
    random.seed(args.seed)

    if not _is_dev_url(args.base_url) and not args.allow_non_dev:
        raise SystemExit(
            f"Refusing to run against non-dev URL: {args.base_url}. "
            "Use --allow-non-dev only if you are 100% sure."
        )

    token = login(args.base_url, args.admin_email, args.admin_password)
    api = ApiClient(args.base_url, token, admin_email=args.admin_email, admin_password=args.admin_password)

    templates = api.post("/api/v1/roles/templates/install-cells-hierarchy")
    installed = templates.get("installed") if isinstance(templates, dict) else None
    if not installed:
        raise RuntimeError("Failed to install role templates (no 'installed' returned).")

    leader_role_id = int(installed["leader"])
    discipler_role_id = int(installed["discipler"])
    network_pastor_role_id = int(installed["network_pastor"])

    password = args.user_password
    email_domain = args.email_domain.lstrip("@")
    prefix = args.prefix.strip().strip(".") or "seed"

    pastor_names = _pick_unique_names(2, prefix="Pastor de Rede")
    discipler_names = _pick_unique_names(4, prefix="Discipulador")
    leader_names = _pick_unique_names(20, prefix="Lider")

    # Create users + members
    pastors = []
    for i, full_name in enumerate(pastor_names, start=1):
        email = f"{prefix}.pastor.rede.{i:02d}@{email_domain}"
        user = _get_or_create_user(api, email=email, full_name=full_name, role_id=network_pastor_role_id, password=password)
        member = _get_or_create_member_for_user(api, user=user, count_start_date=args.count_start_date)
        pastors.append({"user": user, "member": member})

    disciplers = []
    for i, full_name in enumerate(discipler_names, start=1):
        email = f"{prefix}.discipulador.{i:02d}@{email_domain}"
        user = _get_or_create_user(api, email=email, full_name=full_name, role_id=discipler_role_id, password=password)
        member = _get_or_create_member_for_user(api, user=user, count_start_date=args.count_start_date)
        disciplers.append({"user": user, "member": member})

    leaders = []
    for i, full_name in enumerate(leader_names, start=1):
        email = f"{prefix}.lider.{i:02d}@{email_domain}"
        user = _get_or_create_user(api, email=email, full_name=full_name, role_id=leader_role_id, password=password)
        member = _get_or_create_member_for_user(api, user=user, count_start_date=args.count_start_date)
        leaders.append({"user": user, "member": member})

    # Create cells
    cell_names = _pick_unique_names(20, prefix="Celula")
    cells = []
    for i, name in enumerate(cell_names, start=1):
        weekday, _weekday_num = WEEKDAYS[(i - 1) % 5]  # Mon..Fri
        cell = _get_or_create_cell(
            api,
            name=f"Celula {name}",
            weekday=weekday,
            meeting_time=args.meeting_time,
            address=f"Rua {random.choice(['Betel', 'Siao', 'Jerico', 'Emaus', 'Cafarnaum'])}, {100 + i}",
        )
        cells.append(cell)

    # Wire hierarchy first (fast), then optionally seed people/meetings.
    # 2 pastors -> 4 disciplers (2 each) -> 20 leaders (5 cells per discipler)
    cell_assignments: list[dict[str, Any]] = []
    for i, cell in enumerate(cells):
        discipler_idx = i // 5
        pastor_idx = 0 if discipler_idx < 2 else 1

        discipler_member_id = int(disciplers[discipler_idx]["member"]["id"])
        leader_member_id = int(leaders[i]["member"]["id"])
        pastor_member_id = int(pastors[pastor_idx]["member"]["id"])
        cell_id = int(cell["id"])

        _ensure_member_link(api, cell_id=cell_id, member_id=leader_member_id)
        _sync_cell_leadership(
            api,
            cell_id=cell_id,
            discipler_member_id=discipler_member_id,
            leader_member_id=leader_member_id,
            network_pastor_member_id=pastor_member_id,
        )
        # Ensure discipler is supervisor-only (remove from members list if created by backend)
        try:
            api.delete(f"/api/v1/cells/{cell_id}/members/{discipler_member_id}")
        except RuntimeError:
            pass

        cell_assignments.append(
            {
                "cell": cell,
                "cell_id": cell_id,
                "leader_member_id": leader_member_id,
            }
        )

    failed_meetings: list[int] = []

    if not args.skip_people:
        for a in cell_assignments:
            cell = a["cell"]
            cell_id = int(a["cell_id"])
            leader_member_id = int(a["leader_member_id"])

            # Create random people per cell
            # Get current people to avoid duplicating on reruns.
            existing_members = api.get(f"/api/v1/cells/{cell_id}/people", params={"stage": "member"})
            existing_assiduos = api.get(f"/api/v1/cells/{cell_id}/people", params={"stage": "assiduo"})
            existing_visitors = api.get(f"/api/v1/cells/{cell_id}/people", params={"stage": "visitor"})

            visitor_target = random.randint(args.min_visitors, args.max_visitors)
            assiduo_target = random.randint(args.min_assiduos, args.max_assiduos)
            member_target = random.randint(args.min_members, args.max_members)

            visitor_count = max(0, visitor_target - len(existing_visitors or []))
            assiduo_count = max(0, assiduo_target - len(existing_assiduos or []))
            member_count = max(0, member_target - len(existing_members or []))

            used_names = set()

            def unique_person_name(label: str) -> str:
                for _ in range(500):
                    base = random.choice(BIBLICAL_NAMES)
                    nm = f"{base} ({label} {_rand_suffix(3)})"
                    if nm not in used_names:
                        used_names.add(nm)
                        return nm
                return f"{label} {_rand_suffix(6)}"

            for _ in range(member_count):
                m = _create_member(api, full_name=unique_person_name("Membro"), stage="member", count_start_date=args.count_start_date)
                _ensure_member_link(api, cell_id=cell_id, member_id=int(m["id"]))

            for _ in range(assiduo_count):
                m = _create_member(api, full_name=unique_person_name("Assiduo"), stage="assiduo", count_start_date=args.count_start_date)
                _ensure_member_link(api, cell_id=cell_id, member_id=int(m["id"]))

            for _ in range(visitor_count):
                m = _create_member(api, full_name=unique_person_name("Visitante"), stage="visitor", count_start_date=args.count_start_date)
                _ensure_member_link(api, cell_id=cell_id, member_id=int(m["id"]))

    if not args.skip_meetings:
        for a in cell_assignments:
            cell = a["cell"]
            cell_id = int(a["cell_id"])
            leader_member_id = int(a["leader_member_id"])

            # Attendance uses all current people in the cell at the time of seeding.
            existing_members = api.get(f"/api/v1/cells/{cell_id}/people", params={"stage": "member"})
            existing_assiduos = api.get(f"/api/v1/cells/{cell_id}/people", params={"stage": "assiduo"})
            existing_visitors = api.get(f"/api/v1/cells/{cell_id}/people", params={"stage": "visitor"})

            local_people: list[tuple[int, str]] = [(leader_member_id, "member")]
            for row in existing_members or []:
                local_people.append((int(row["id"]), "member"))
            for row in existing_assiduos or []:
                local_people.append((int(row["id"]), "assiduo"))
            for row in existing_visitors or []:
                local_people.append((int(row["id"]), "visitor"))

            for month in (2, 3, 4):
                start, end = _month_date_range(args.year, month)
                existing = _list_meetings(api, cell_id=cell_id, start=start, end=end)
                existing_by_date = {row.get("meeting_date"): row for row in (existing or [])}

                # Find weekday number from cell weekday
                weekday_str = (cell.get("weekday") or "wednesday").lower()
                weekday_num = next((num for (slug, num) in WEEKDAYS if slug == weekday_str), 2)
                dates = _iter_weekday_dates(start, end, weekday_num)

                for d in dates:
                    meeting = existing_by_date.get(d.isoformat())
                    if not meeting:
                        theme = random.choice(CELL_THEMES)
                        meeting = api.post(
                            f"/api/v1/cells/{cell_id}/meetings",
                            json={
                                "meeting_date": d.isoformat(),
                                "theme": theme,
                                "notes": "",
                            },
                        )

                    meeting_id = int(meeting["id"])

                    items = []
                    for mid, stage in local_people:
                        if stage == "visitor":
                            p_present = 0.45
                        elif stage == "assiduo":
                            p_present = 0.62
                        else:
                            p_present = 0.74

                        r = random.random()
                        if r < p_present:
                            status = "present"
                        elif r < p_present + 0.07:
                            status = "justified"
                        else:
                            status = "absent"
                        items.append({"member_id": mid, "attendance_status": status, "notes": None})

                    try:
                        _upsert_attendance(api, meeting_id=meeting_id, items=items)
                    except RuntimeError:
                        failed_meetings.append(meeting_id)
                        continue

    print("\nSeed concluido.")
    print(f"Base URL: {args.base_url}")
    print(f"Senha dos usuarios seed: {password}")
    print("Usuarios criados (exemplos):")
    print(f"- Pastores de rede: {len(pastors)}")
    print(f"- Discipuladores: {len(disciplers)}")
    print(f"- Lideres: {len(leaders)}")
    print(f"- Celulas: {len(cells)}")
    if failed_meetings:
        uniq = sorted(set(failed_meetings))
        print(f"\nAtencao: falhou ao inserir frequencia em {len(uniq)} reuniao(oes).")
        print("Reexecute o seed para tentar novamente (ele continua de onde parou).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed dev data for Cells org chart (dev only).")
    parser.add_argument("--base-url", required=True, help="Ex: http://localhost:8000 ou https://dev.jpmit.top")
    parser.add_argument("--admin-email", default=os.getenv("ADMIN_EMAIL") or os.getenv("FIRST_SUPERUSER"))
    parser.add_argument("--admin-password", default=os.getenv("ADMIN_PASSWORD") or os.getenv("FIRST_SUPERUSER_PASSWORD"))
    parser.add_argument("--allow-non-dev", action="store_true", help="Permite rodar fora de dev (nao recomendado).")

    parser.add_argument("--email-domain", default="seed.dev", help="Dominio para emails seed.")
    parser.add_argument("--prefix", default="seed", help="Prefixo para emails seed (ex: seed).")
    parser.add_argument("--user-password", default="SeedPass123!", help="Senha usada nos usuarios seed.")
    parser.add_argument("--seed", type=int, default=20260413)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--meeting-time", default="19:30:00")
    parser.add_argument("--count-start-date", default="2026-01-15")

    parser.add_argument("--min-visitors", type=int, default=2)
    parser.add_argument("--max-visitors", type=int, default=6)
    parser.add_argument("--min-assiduos", type=int, default=3)
    parser.add_argument("--max-assiduos", type=int, default=8)
    parser.add_argument("--min-members", type=int, default=6)
    parser.add_argument("--max-members", type=int, default=12)
    parser.add_argument("--skip-people", action="store_true", help="Nao cria membros aleatorios por celula.")
    parser.add_argument("--skip-meetings", action="store_true", help="Nao cria reunioes nem frequencia (somente organograma).")

    args = parser.parse_args()
    if not args.admin_email or not args.admin_password:
        raise SystemExit("Missing admin credentials. Provide --admin-email/--admin-password or set ADMIN_EMAIL/ADMIN_PASSWORD.")
    seed(args)


if __name__ == "__main__":
    main()
