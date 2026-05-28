import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pricing import bond_price_duration_convexity, fx_forward_rate

def test_fx_forward_rate():
    assert round(fx_forward_rate(1.3712, 42), 4) == 1.3754

def test_bond_price_reasonable():
    price, duration, convexity = bond_price_duration_convexity(
        face=100,
        coupon_rate=0.03,
        ytm=0.03,
        maturity_years=5,
        freq=2
    )
    assert 99.0 < price < 101.0
    assert duration > 0
    assert convexity > 0
