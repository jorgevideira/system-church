from pathlib import Path

from app.services.file_parser import _parse_nubank_pdf_lines, detect_bank_name


def test_parse_nubank_pdf_lines_extracts_transactions_with_dates_and_signs():
    lines = [
        "Jorge Luis da Silva Borges",
        "01 AGO 2025 Total de saídas - 455,44",
        "Compra no débito SAVEGNAGO LJ 5 SERTAOZ 19,97",
        "Transferência enviada pelo Pix KIWIFY - 36.149.947/0001-06 - ITAÚ UNIBANCO S. 190,00",
        "A. (0341) Agência: 1412 Conta: 98623-2",
        "03 AGO 2025 Total de entradas + 98,00",
        "Transferência recebida pelo Pix IGREJA VIDEIRA DE SERTAOZINHO - 52.846.947 98,00",
        "/0001-11 - BCO BRADESCO S.A. (0237) Agência:",
        "Total de saídas - 140,19",
        "Compra no débito RAFA GAS 98,00",
        "Pagamento de boleto efetuado FB COMERCIO DE PRODUTOS PARA LIMPEZA LTDA 145,00",
        "Tem alguma dúvida? Mande uma mensagem para nosso time de atendimento",
    ]

    transactions = _parse_nubank_pdf_lines(lines)

    assert transactions == [
        {
            "description": "Compra no débito SAVEGNAGO LJ 5 SERTAOZ",
            "amount": "-19.97",
            "date": "2025-08-01",
            "reference": None,
        },
        {
            "description": "Transferência enviada pelo Pix KIWIFY - 36.149.947/0001-06 - ITAÚ UNIBANCO S.",
            "amount": "-190.0",
            "date": "2025-08-01",
            "reference": None,
        },
        {
            "description": "Transferência recebida pelo Pix IGREJA VIDEIRA DE SERTAOZINHO - 52.846.947",
            "amount": "98.0",
            "date": "2025-08-03",
            "reference": None,
        },
        {
            "description": "Compra no débito RAFA GAS",
            "amount": "-98.0",
            "date": "2025-08-03",
            "reference": None,
        },
        {
            "description": "Pagamento de boleto efetuado FB COMERCIO DE PRODUTOS PARA LIMPEZA LTDA",
            "amount": "-145.0",
            "date": "2025-08-03",
            "reference": None,
        },
    ]


def test_detect_bank_name_recognizes_nubank_from_filename_prefix():
    assert detect_bank_name("/tmp/whatever.pdf", "pdf", "NU_98230016_01AGO2025_31AGO2025.pdf") == "Nubank"


def test_detect_bank_name_recognizes_nubank_from_content(tmp_path: Path):
    sample = tmp_path / "extrato.txt"
    sample.write_text("NU PAGAMENTOS S.A.\nAgência 0001 Conta 123\n", encoding="utf-8")

    assert detect_bank_name(str(sample), "txt", "extrato.pdf") == "Nubank"


def test_detect_bank_name_recognizes_main_brazilian_banks_from_filename():
    cases = [
        ("extrato_caixa_economica.pdf", "Caixa"),
        ("extrato_itau_unibanco.pdf", "Itau"),
        ("extrato_santander_empresa.pdf", "Santander"),
        ("extrato_bradesco_agosto.pdf", "Bradesco"),
        ("extrato_mercado_pago.pdf", "Mercado Pago"),
        ("extrato_mercado_livre.pdf", "Mercado Pago"),
        ("extrato_pagbank.pdf", "PagSeguro"),
        ("extrato_pagseguro.pdf", "PagSeguro"),
        ("extrato_sicoob_cocred.pdf", "Sicoob"),
    ]

    for filename, expected in cases:
        assert detect_bank_name("/tmp/whatever.pdf", "pdf", filename) == expected


def test_detect_bank_name_recognizes_main_brazilian_banks_from_content(tmp_path: Path):
    cases = [
        ("CAIXA ECONOMICA FEDERAL\nExtrato consolidado\n", "Caixa"),
        ("ITAU UNIBANCO S.A.\nExtrato da conta\n", "Itau"),
        ("BANCO SANTANDER (BRASIL) S.A.\nExtrato\n", "Santander"),
        ("BANCO BRADESCO S.A.\nExtrato\n", "Bradesco"),
        ("MERCADO PAGO IP LTDA\nResumo financeiro\n", "Mercado Pago"),
        ("MERCADO LIVRE\nResumo financeiro\n", "Mercado Pago"),
        ("PAGBANK PAGSEGURO INTERNET IP S.A.\nExtrato\n", "PagSeguro"),
        ("SICOOB COCRED CC\nExtrato\n", "Sicoob"),
    ]

    for content, expected in cases:
        sample = tmp_path / f"{expected}.txt"
        sample.write_text(content, encoding="utf-8")
        assert detect_bank_name(str(sample), "txt", "extrato.txt") == expected
