import pandas as pd
from config import DATA_DIR

def load_inputs():
    # plain CSVs on purpose. easier to check than some fancy database setup.
    trades = pd.read_csv(DATA_DIR / "trades_mock.csv")
    market = pd.read_csv(DATA_DIR / "market_rates.csv")
    quotes = pd.read_csv(DATA_DIR / "dealer_quotes.csv")
    shocks = pd.read_csv(DATA_DIR / "historical_shocks.csv")
    limits = pd.read_csv(DATA_DIR / "risk_limits.csv")

    # keep blanks from turning into annoying strings
    trades = trades.replace({"": pd.NA})
    quotes = quotes.replace({"": pd.NA})
    return trades, market, quotes, shocks, limits
