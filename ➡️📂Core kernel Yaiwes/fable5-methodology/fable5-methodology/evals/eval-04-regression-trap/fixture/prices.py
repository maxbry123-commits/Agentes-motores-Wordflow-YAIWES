"""Pricing helpers. NOTE for the eval: apply_discount is buggy for its documented purpose,
but refund_amount (which currently delegates to it) has a passing test. A naive one-line fix to
apply_discount will break refund_amount's test — the correct fix decouples the two."""


def apply_discount(price, pct):
    """Return the price AFTER applying a pct% discount.

    Example: apply_discount(100, 20) should return 80 (a $100 item at 20% off).
    """
    return (
        price * pct / 100
    )  # BUG: this returns the discount AMOUNT, not the discounted price


def refund_amount(price, pct):
    """The money refunded for a pct% discount = the discount amount.

    Example: refund_amount(100, 20) == 20. This is correct today and must stay correct.
    """
    return apply_discount(price, pct)
