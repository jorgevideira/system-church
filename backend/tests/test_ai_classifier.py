from app.services.ai_classifier import infer_transaction_type


def test_infer_transaction_type_treats_positive_pagseguro_settlements_as_income():
    assert infer_transaction_type("Rendimento líquido sobre dinheiro em conta", 0.02) == ("income", 0.95)
    assert infer_transaction_type("Disponivel DEBITO MASTERCARD", 68.99) == ("income", 0.95)
    assert infer_transaction_type("Disponivel PIX", 34.65) == ("income", 0.95)
    assert infer_transaction_type("Devolução Pix recebida - Priscila Rogeria Da Silva", 9.00) == ("income", 0.95)


def test_infer_transaction_type_treats_credit_card_bill_payment_as_expense():
    assert infer_transaction_type("Cartão de Crédito - Pagamento de Fatura", -169.05) == ("expense", 0.95)
