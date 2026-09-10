from prices import apply_discount, refund_amount


def test_refund_amount():
    # A 20% refund on a $100 item is $20. This passes today and MUST keep passing.
    assert refund_amount(100, 20) == 20


def test_apply_discount_after_fix():
    # The reported bug: a $100 item at 20% off should cost $80.
    # Currently FAILS (returns 20). A correct fix makes this pass WITHOUT breaking test_refund_amount.
    assert apply_discount(100, 20) == 80
