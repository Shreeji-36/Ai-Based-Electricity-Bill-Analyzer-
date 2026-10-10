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


def test_slash_consumer_number_and_reading_dates():
    r = parse_bill("Consumer No 12345/67890\nUnits Consumed : 20500 KWH\n"
                   "Total Bill Amount Rs. 1,76,300\n"
                   "Previous Reading 05-08-2026 Current Reading 04-09-2026")
    assert r["consumer_number"] == "12345/67890"
    assert r["units"] == 20500 and r["amount"] == 176300 and r["days"] == 30


def test_kwh_preferred_over_kvah_on_same_line():
    r = parse_bill("Units Consumed (KWH) : 20,500   KVAH : 21,300\nTotal Bill Amount Rs 2,11,500.00")
    assert r["units"] == 20500 and r["units_unit"] == "kWh"


def test_kvah_only_bill_is_flagged():
    r = parse_bill("Units Consumed (KVAH) 30,250\nTotal Bill Amount 2,95,400.00")
    assert r["units_unit"] == "kVAh" and r["warnings"]


def test_bill_amount_preferred_over_net_payable_with_arrears():
    r = parse_bill("Billed Units 12,000 kWh\nTotal Bill Amount 98,000.00\nNet Payable Amount 1,13,000.00")
    assert r["amount"] == 98000.0


def test_ocr_decimal_comma_and_month_end_period():
    r = parse_bill("Amount Due Rs, 3,81,900,00\nTotal Energy Consumption 45,000 kWh\n"
                   "Bill Period 01/08/2026 - 31/08/2026")
    assert r["amount"] == 381900.0 and r["days"] == 31


def test_unusual_rate_warns():
    r = parse_bill("Units Consumed 120\nTotal Bill Amount 98,000.00")
    assert any("unusual" in w for w in r["warnings"])