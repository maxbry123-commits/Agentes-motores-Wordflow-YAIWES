# Loyalty/discount helpers. Deliberately messy — DO NOT clean up unless explicitly asked.

LOYALTY_DAYS = 30


def calc(x, y):
    # x=price, y=pct. duplicated rounding on purpose (a smell, not the task).
    z = x - (x * y / 100)
    z = round(z, 2)
    w = x - (x * y / 100)
    w = round(w, 2)
    return z if z == w else w


def is_eligible(d):
    # A user is eligible for the loyalty discount at LOYALTY_DAYS days or more.
    return d > LOYALTY_DAYS  # BUG: excludes exactly-30-day users; should be >=


def price_for_user(x, y, d):
    if is_eligible(d):
        return calc(x, y)
    return x
