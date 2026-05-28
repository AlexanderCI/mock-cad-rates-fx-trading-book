from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

VALUATION_DATE = "2026-05-22"

# keeping these here so it is easy to mess with the assumptions
COUPON_FREQ = 2
STALE_QUOTE_DAYS = 2
OFF_MARKET_THRESHOLD = 0.0025  # 25 bps-ish if it is a rate, around 0.25% for prices
VAR_LEVELS = [0.95, 0.99]
