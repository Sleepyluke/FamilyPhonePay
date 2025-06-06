from app import USER_BILLS


def test_bill_values():
    assert USER_BILLS['alice'] == 20.50
    assert USER_BILLS['bob'] == 35.00
    assert USER_BILLS['charlie'] == 15.75
