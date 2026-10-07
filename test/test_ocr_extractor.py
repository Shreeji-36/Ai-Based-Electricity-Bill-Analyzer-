from app.extractor import parse_bill  # resolved via ocr/ on sys.path

SAMPLE = """
Consumer No: GJ1234567
Bill Date: 05/09/2026
Billing Period 05/08/2026 to 04/09/2026
Tariff Category: HT-I Industrial
Total Units Consumed 20,500
Total Amount Payable 1,76,300.00
"""


def test_parse_core_fields():
    r = parse_bill(SAMPLE)
    assert r["consumer_number"] == "GJ1234567"
    assert r["units"] == 20500
    assert r["amount"] == 176300.0
    assert r["days"] == 30
    assert r["confidence"] == 1.0


def test_parse_empty_text():
    assert parse_bill("nothing useful")["confidence"] == 0.0