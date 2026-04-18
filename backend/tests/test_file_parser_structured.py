from pathlib import Path

from app.services.file_parser import _parse_bradesco_pdf_lines, _parse_pagseguro_pdf_lines, parse_csv, parse_ofx


def test_parse_csv_handles_semicolon_debit_credit_and_sep_header(tmp_path: Path):
    sample = tmp_path / "extrato.csv"
    sample.write_text(
        "sep=;\n"
        "Data;Descrição;Débito;Crédito;Documento\n"
        "01/08/2025;Compra Mercado;19,90;;123\n"
        "02/08/2025;Pix recebido João;;150,00;456\n",
        encoding="utf-8",
    )

    transactions = parse_csv(str(sample))

    assert transactions == [
        {
            "description": "Compra Mercado",
            "amount": "-19.9",
            "date": "2025-08-01",
            "reference": "123",
        },
        {
            "description": "Pix recebido João",
            "amount": "150.0",
            "date": "2025-08-02",
            "reference": "456",
        },
    ]


def test_parse_csv_handles_latin1_and_type_based_sign(tmp_path: Path):
    sample = tmp_path / "extrato_latin1.csv"
    sample.write_bytes(
        (
            "data,descrição,valor,tipo,documento\n"
            "03/08/2025 10:30,Depósito identificado,-200.50,Crédito,abc\n"
            "04/08/2025 11:00,Pagamento fornecedor,350.75,Débito,def\n"
        ).encode("cp1252")
    )

    transactions = parse_csv(str(sample))

    assert transactions == [
        {
            "description": "Depósito identificado",
            "amount": "200.5",
            "date": "2025-08-03",
            "reference": "abc",
        },
        {
            "description": "Pagamento fornecedor",
            "amount": "-350.75",
            "date": "2025-08-04",
            "reference": "def",
        },
    ]


def test_parse_ofx_xml_fallback_extracts_transactions(tmp_path: Path):
    sample = tmp_path / "extrato.ofx"
    sample.write_text(
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        "<OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST>"
        "<STMTTRN><TRNAMT>-19.90</TRNAMT><DTPOSTED>20250801120000</DTPOSTED>"
        "<FITID>1</FITID><NAME>Compra Mercado</NAME></STMTTRN>"
        "<STMTTRN><TRNAMT>150.00</TRNAMT><DTPOSTED>20250802120000</DTPOSTED>"
        "<FITID>2</FITID><MEMO>Pix recebido Joao</MEMO></STMTTRN>"
        "</BANKTRANLIST></STMTRS></STMTTRNRS></BANKMSGSRSV1></OFX>",
        encoding="utf-8",
    )

    transactions = parse_ofx(str(sample))

    assert transactions == [
        {
            "description": "Compra Mercado",
            "amount": "-19.90",
            "date": "2025-08-01",
            "reference": "1",
        },
        {
            "description": "Pix recebido Joao",
            "amount": "150.00",
            "date": "2025-08-02",
            "reference": "2",
        },
    ]


def test_parse_csv_handles_mercado_pago_statement_with_summary_block(tmp_path: Path):
    sample = tmp_path / "mercado_pago.csv"
    sample.write_text(
        "INITIAL_BALANCE;CREDITS;DEBITS;FINAL_BALANCE\n"
        "0,00;1,10;-1,10;0,00\n"
        "\n"
        "RELEASE_DATE;TRANSACTION_TYPE;REFERENCE_ID;TRANSACTION_NET_AMOUNT;PARTIAL_BALANCE\n"
        "09-04-2026;Liberação de dinheiro ;153978326594;0,10;0,10\n"
        "09-04-2026;Débito por dívida Empréstimos Mercado Pago;3027252142;-0,10;0,00\n"
        "09-04-2026;Pagamento com Código QR Pix Jorge Luis da Silva Borges;153325528167;0,20;0,20\n",
        encoding="utf-8",
    )

    transactions = parse_csv(str(sample))

    assert transactions == [
        {
            "description": "Liberação de dinheiro",
            "amount": "0.10",
            "date": "2026-04-09",
            "reference": "153978326594",
        },
        {
            "description": "Débito por dívida Empréstimos Mercado Pago",
            "amount": "-0.10",
            "date": "2026-04-09",
            "reference": "3027252142",
        },
        {
            "description": "Pagamento com Código QR Pix Jorge Luis da Silva Borges",
            "amount": "0.20",
            "date": "2026-04-09",
            "reference": "153325528167",
        },
    ]


def test_parse_csv_keeps_pagseguro_credit_card_bill_payment_as_expense(tmp_path: Path):
    sample = tmp_path / "pagseguro.csv"
    sample.write_text(
        "CODIGO DA TRANSACAO;DATA;TIPO;DESCRICAO;VALOR\n"
        "1;05/02/2026;Cartão de Crédito;Pagamento de Fatura;-169,05 \n"
        "2;05/02/2026;Cartão de Crédito;Pagamento de Fatura;-25,61 \n"
        "3;07/02/2026;Pix recebido;Igreja Videia De Sertaozinho;200,00 \n",
        encoding="utf-8",
    )

    transactions = parse_csv(str(sample))

    assert transactions == [
        {
            "description": "Pagamento de Fatura",
            "amount": "-169.05",
            "date": "2026-02-05",
            "reference": "1",
        },
        {
            "description": "Pagamento de Fatura",
            "amount": "-25.61",
            "date": "2026-02-05",
            "reference": "2",
        },
        {
            "description": "Igreja Videia De Sertaozinho",
            "amount": "200.00",
            "date": "2026-02-07",
            "reference": "3",
        },
    ]


def test_parse_csv_preserves_pagseguro_transaction_code_as_reference_for_repeated_rows(tmp_path: Path):
    sample = tmp_path / "pagseguro_repeat.csv"
    sample.write_text(
        "CODIGO DA TRANSACAO;DATA;TIPO;DESCRICAO;VALOR\n"
        "abc-1;13/04/2026;Pix recebido;Tainá Vitória De Oliveira Martins;25,00 \n"
        "abc-2;13/04/2026;Pix recebido;Tainá Vitória De Oliveira Martins;25,00 \n",
        encoding="utf-8",
    )

    transactions = parse_csv(str(sample))

    assert transactions == [
        {
            "description": "Tainá Vitória De Oliveira Martins",
            "amount": "25.00",
            "date": "2026-04-13",
            "reference": "abc-1",
        },
        {
            "description": "Tainá Vitória De Oliveira Martins",
            "amount": "25.00",
            "date": "2026-04-13",
            "reference": "abc-2",
        },
    ]


def test_parse_pagseguro_pdf_lines_infers_opening_balance_and_keeps_duplicate_lines():
    lines = [
        "16/01/2026 Pix enviado - Jorge Luis Da Silva Borges -R$ 100,00",
        "16/01/2026 Saldo do dia R$ 389,83",
        "13/04/2026 Pix recebido - Tainá Vitória De Oliveira Martins R$ 25,00",
        "13/04/2026 Pix recebido - Tainá Vitória De Oliveira Martins R$ 25,00",
    ]

    transactions = _parse_pagseguro_pdf_lines(lines)

    assert transactions == [
        {
            "description": "Saldo inicial inferido do extrato",
            "amount": "489.83",
            "date": "2026-01-15",
            "reference": "pagseguro-opening-2026-01-15",
        },
        {
            "description": "Pix enviado - Jorge Luis Da Silva Borges",
            "amount": "-100.00",
            "date": "2026-01-16",
            "reference": "pagseguro-pdf-1",
        },
        {
            "description": "Pix recebido - Tainá Vitória De Oliveira Martins",
            "amount": "25.00",
            "date": "2026-04-13",
            "reference": "pagseguro-pdf-3",
        },
        {
            "description": "Pix recebido - Tainá Vitória De Oliveira Martins",
            "amount": "25.00",
            "date": "2026-04-13",
            "reference": "pagseguro-pdf-4",
        },
    ]


def test_parse_csv_handles_bradesco_statement_with_credit_debit_columns_and_ignores_extra_sections(tmp_path: Path):
    sample = tmp_path / "bradesco.csv"
    sample.write_bytes(
        (
            "\n;Extrato de: Agência: 185  Conta: 144056-0\r\n"
            "Data;Lançamento;Dcto.;Crédito (R$);Débito (R$);Saldo (R$)\r"
            "30/01/2026;SALDO ANTERIOR;;;;13.882,78\r"
            "02/02/2026;TRANSFERENCIA PIX REM: ARTHUR LIMA DA SILVA 01/02;938274;15,00;;13.897,78\r"
            "02/02/2026;TRANSFERENCIA PIX DES: MARCOS ROBERTO FILIPI 02/02;1907273;;-55,50;19.114,08\r"
            "05/02/2026;PAGTO ELETRON  COBRANCA ALUGUEL;108;;-2.555,64;17.170,67\r"
        "13/04/2026;PIX QR CODE ESTATICO DES: PIX Marketplace 13/04;1521402;;-51,27;16.488,13\r"
        "Total;;;44.174,94;-41.569,59;16.488,13\r\n"
        ";Últimos Lançamentos\r\n"
        "Data;Lançamento;Dcto.;Crédito (R$);Débito (R$);Saldo (R$)\r"
        "13/04/2026;SALDO ANTERIOR;;;;16.488,11\r"
        "15/04/2026;TARIFA BANCARIA CESTA PJ FACIL 1;10426;;-168,50;16.319,63\r\n"
    ).encode("cp1252")
)

    transactions = parse_csv(str(sample))

    assert transactions == [
        {
            "description": "TRANSFERENCIA PIX REM: ARTHUR LIMA DA SILVA 01/02",
            "amount": "15.00",
            "date": "2026-02-02",
            "reference": "938274",
        },
        {
            "description": "TRANSFERENCIA PIX DES: MARCOS ROBERTO FILIPI 02/02",
            "amount": "-55.50",
            "date": "2026-02-02",
            "reference": "1907273",
        },
        {
            "description": "PAGTO ELETRON  COBRANCA ALUGUEL",
            "amount": "-2555.64",
            "date": "2026-02-05",
            "reference": "108",
        },
        {
            "description": "PIX QR CODE ESTATICO DES: PIX Marketplace 13/04",
            "amount": "-51.27",
            "date": "2026-04-13",
            "reference": "1521402",
        },
        {
            "description": "TARIFA BANCARIA CESTA PJ FACIL 1",
            "amount": "-168.50",
            "date": "2026-04-15",
            "reference": "10426",
        },
    ]


def test_parse_bradesco_pdf_lines_handles_inline_entries_and_stops_before_latest_section():
    lines = [
        "Agência | Conta Total Disponível (R$) Total (R$)",
        "00185 | 0144056-0 16.322,42 16.322,42",
        "Extrato de: Ag: 185 | CC: 0144056-0 | Entre 01/02/2026 e 14/04/2026",
        "Data Lançamento Dcto. Crédito (R$) Débito (R$) Saldo (R$)",
        "30/01/2026 SALDO ANTERIOR 13.882,78",
        "TRANSFERENCIA PIX",
        "REM: ANDERSON DONATO TORRE 2346042 100,00 17.883,83",
        "08/02",
        "24/02/2026 RENTAB.INVEST FACILCRED* 331927 0,60 18.956,85",
        "TRANSFERENCIA PIX",
        "10/03/2026 REM: ANDERSON DONATO TORRE 1227578 100,00 18.336,56",
        "10/03",
        "TRANSFERENCIA PIX",
        "DES: IGREJA VIDEIA DE SERT 07/02 1026394 -200,00 17.686,23",
        "TRANSFERENCIA PIX",
        "TRANSFERENCIA PIX 1919541 300,00 31.468,34",
        "REM: CARLA APARECIDA MONTA 16/03",
        "Últimos Lançamentos",
        "13/04/2026 SALDO ANTERIOR 16.488,11",
        "RENTAB.INVEST FACILCRED* 2619446 0,02 16.488,13",
        "TARIFA BANCARIA",
        "15/04/2026 10426 -168,50 16.319,63",
        "CESTA PJ FACIL 1",
        "Saldos Invest Fácil / Plus",
    ]

    transactions = _parse_bradesco_pdf_lines(lines)

    assert transactions == [
        {
            "description": "TRANSFERENCIA PIX REM: ANDERSON DONATO TORRE 08/02",
            "amount": "100.00",
            "date": "2026-01-30",
            "reference": "2346042",
        },
        {
            "description": "RENTAB.INVEST FACILCRED*",
            "amount": "0.60",
            "date": "2026-02-24",
            "reference": "331927",
        },
        {
            "description": "TRANSFERENCIA PIX REM: ANDERSON DONATO TORRE 10/03",
            "amount": "100.00",
            "date": "2026-03-10",
            "reference": "1227578",
        },
        {
            "description": "TRANSFERENCIA PIX DES: IGREJA VIDEIA DE SERT 07/02",
            "amount": "-200.00",
            "date": "2026-03-10",
            "reference": "1026394",
        },
        {
            "description": "TRANSFERENCIA PIX REM: CARLA APARECIDA MONTA 16/03",
            "amount": "300.00",
            "date": "2026-03-10",
            "reference": "1919541",
        },
        {
            "description": "RENTAB.INVEST FACILCRED*",
            "amount": "0.02",
            "date": "2026-04-13",
            "reference": "2619446",
        },
        {
            "description": "TARIFA BANCARIA CESTA PJ FACIL 1",
            "amount": "-168.50",
            "date": "2026-04-15",
            "reference": "10426",
        },
    ]


def test_parse_bradesco_pdf_lines_handles_unaccented_section_headers_and_keeps_latest_entries():
    lines = [
        "Agencia | Conta Total Disponivel (R$) Total (R$)",
        "00185 | 0144056-0 16.322,42 16.322,42",
        "Extrato de: Ag: 185 | CC: 0144056-0 | Entre 01/02/2026 e 14/04/2026",
        "Data Lancamento Dcto. Credito (R$) Debito (R$) Saldo (R$)",
        "30/01/2026 SALDO ANTERIOR 13.882,78",
        "PIX QR CODE ESTATICO",
        "1521402 -51,27 16.488,13",
        "DES: PIX Marketplace 13/04",
        "Ultimos Lancamentos",
        "Data Lancamento Dcto. Credito (R$) Debito (R$) Saldo (R$)",
        "13/04/2026 SALDO ANTERIOR 16.488,11",
        "RENTAB.INVEST FACILCRED* 2619446 0,02 16.488,13",
        "TARIFA BANCARIA",
        "15/04/2026 10426 -168,50 16.319,63",
        "CESTA PJ FACIL 1",
        "Saldos Invest Facil / Plus",
        "14/04/2026 SALDO INVEST FACIL 16.490,56",
    ]

    transactions = _parse_bradesco_pdf_lines(lines)

    assert transactions == [
        {
            "description": "PIX QR CODE ESTATICO DES: PIX Marketplace 13/04",
            "amount": "-51.27",
            "date": "2026-01-30",
            "reference": "1521402",
        },
        {
            "description": "RENTAB.INVEST FACILCRED*",
            "amount": "0.02",
            "date": "2026-04-13",
            "reference": "2619446",
        },
        {
            "description": "TARIFA BANCARIA CESTA PJ FACIL 1",
            "amount": "-168.50",
            "date": "2026-04-15",
            "reference": "10426",
        },
    ]
