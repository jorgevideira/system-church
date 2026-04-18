from app.services import statement_ai_parser


def test_load_transactions_from_response_normalizes_ollama_output():
    response_text = """
    {
      "transactions": [
        {
          "date": "14/04/2026",
          "description": "Pix recebido Joao",
          "amount": "150,90",
          "reference": "abc-123"
        },
        {
          "date": "2026-04-13",
          "description": "Compra no debito Mercado",
          "amount": "-45.20"
        }
      ]
    }
    """

    transactions = statement_ai_parser._load_transactions_from_response(response_text)

    assert transactions == [
        {
            "description": "Pix recebido Joao",
            "date": "2026-04-14",
            "amount": "150.90",
            "reference": "abc-123",
        },
        {
            "description": "Compra no debito Mercado",
            "date": "2026-04-13",
            "amount": "-45.20",
            "reference": None,
        },
    ]


def test_load_transactions_from_response_fixes_amount_sign_by_description_hint():
    response_text = """
    {
      "transactions": [
        {
          "date": "2026-04-14",
          "description": "Pix recebido Maria",
          "amount": "-150.90"
        },
        {
          "date": "2026-04-13",
          "description": "Compra no debito Mercado",
          "amount": "45.20"
        }
      ]
    }
    """

    transactions = statement_ai_parser._load_transactions_from_response(response_text)

    assert transactions == [
        {
            "description": "Pix recebido Maria",
            "date": "2026-04-14",
            "amount": "150.90",
            "reference": None,
        },
        {
            "description": "Compra no debito Mercado",
            "date": "2026-04-13",
            "amount": "-45.20",
            "reference": None,
        },
    ]
