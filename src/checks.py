import pandas as pd
from config import VALUATION_DATE, STALE_QUOTE_DAYS

def check_trade_blotter(trades: pd.DataFrame) -> pd.DataFrame:
    issues = []

    duplicated = trades[trades["trade_id"].duplicated(keep=False)]
    for _, row in duplicated.iterrows():
        issues.append([row["trade_id"], "duplicate trade id", "same trade id appears more than once"])

    required_by_type = {
        "GOC_BOND": ["quantity", "coupon_rate", "maturity_years", "trade_price", "current_price", "current_yield"],
        "FX_SPOT": ["notional", "fx_pair", "trade_fx_rate", "current_fx_rate"],
        "FX_FORWARD": ["notional", "fx_pair", "trade_fx_rate", "current_fx_rate", "forward_points"],
        "IRS": ["notional", "fixed_rate", "curve_tenor_years"],
        "BOND_FORWARD": ["quantity", "coupon_rate", "maturity_years", "contract_price", "current_yield"],
        "IR_FUTURE": ["quantity", "futures_price", "notional"],
    }

    for _, row in trades.iterrows():
        trade_type = row["instrument_type"]
        for col in required_by_type.get(trade_type, []):
            if pd.isna(row.get(col)):
                issues.append([row["trade_id"], f"missing {col}", f"{trade_type} needs this input"])

    return pd.DataFrame(issues, columns=["trade_id", "issue", "comment"])


def check_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    if quotes.empty:
        return pd.DataFrame(columns=["trade_id", "issue", "comment"])

    q = quotes.copy()
    q["quote_date"] = pd.to_datetime(q["quote_date"])
    val_date = pd.to_datetime(VALUATION_DATE)

    issues = []
    for _, row in q.iterrows():
        age = (val_date - row["quote_date"]).days
        if age > STALE_QUOTE_DAYS:
            issues.append([row["trade_id"], "stale quote", f"{row['dealer']} quote is {age} days old"])
        if pd.isna(row["bid"]) or pd.isna(row["ask"]):
            issues.append([row["trade_id"], "missing bid/ask", f"{row['dealer']} has incomplete quote"])
        elif row["bid"] > row["ask"]:
            issues.append([row["trade_id"], "bad market", f"{row['dealer']} bid is above ask"])

    return pd.DataFrame(issues, columns=["trade_id", "issue", "comment"])
