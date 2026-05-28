import pandas as pd
from config import OUTPUT_DIR, VALUATION_DATE, OFF_MARKET_THRESHOLD

def compare_dealer_quotes(trades: pd.DataFrame, quotes: pd.DataFrame):
    rows = []

    side_map = trades.set_index("trade_id")["side"].to_dict()

    for trade_id, group in quotes.groupby("trade_id"):
        side = side_map.get(trade_id, "BUY")
        g = group.copy()
        g["executable_quote"] = g["ask"] if side in ["BUY", "PAY_FIXED"] else g["bid"]
        median_quote = g["executable_quote"].median()

        for _, row in g.iterrows():
            diff = float(row["executable_quote"]) - float(median_quote)
            off_market = abs(diff) > abs(median_quote) * OFF_MARKET_THRESHOLD
            rows.append({
                "trade_id": trade_id,
                "dealer": row["dealer"],
                "side": side,
                "bid": row["bid"],
                "ask": row["ask"],
                "mid": row["mid"],
                "executable_quote": row["executable_quote"],
                "diff_vs_median": diff,
                "off_market_flag": bool(off_market),
                "quote_date": row["quote_date"],
                "notes": row["notes"],
            })

    out = pd.DataFrame(rows)
    if not out.empty:
        out["rank_for_trade"] = out.groupby("trade_id")["executable_quote"].rank(
            ascending=True, method="dense"
        )
    return out


def write_outputs(blotter_issues, position_report, quote_report, risk_summary, shock_report, limit_breaches):
    OUTPUT_DIR.mkdir(exist_ok=True)

    blotter_issues.to_csv(OUTPUT_DIR / "blotter_issues.csv", index=False)
    position_report.to_csv(OUTPUT_DIR / "position_report.csv", index=False)
    quote_report.to_csv(OUTPUT_DIR / "dealer_quote_comparison.csv", index=False)
    risk_summary.to_csv(OUTPUT_DIR / "risk_summary.csv", index=False)
    shock_report.to_csv(OUTPUT_DIR / "shock_pnl_report.csv", index=False)
    limit_breaches.to_csv(OUTPUT_DIR / "limit_breaches.csv", index=False)

    pnl = position_report[[
        "trade_id", "instrument_type", "book", "counterparty",
        "position_value", "initial_value", "mtm_pnl", "pricing_note"
    ]].copy()
    pnl.to_csv(OUTPUT_DIR / "pnl_report.csv", index=False)

    write_desk_pack(position_report, risk_summary, blotter_issues, limit_breaches)


def write_desk_pack(position_report, risk_summary, blotter_issues, limit_breaches):
    total_pnl = position_report["mtm_pnl"].sum()
    net_dv01 = position_report["dv01"].sum()
    fx_exp = position_report["fx_exposure_cad"].sum()

    lines = []
    lines.append(f"Mock desk pack - valuation date {VALUATION_DATE}")
    lines.append("")
    lines.append("quick numbers")
    lines.append(f"total mtm pnl: {total_pnl:,.2f}")
    lines.append(f"net dv01: {net_dv01:,.2f}")
    lines.append(f"net fx exposure: {fx_exp:,.2f}")
    lines.append("")
    lines.append("risk summary")
    for _, row in risk_summary.iterrows():
        lines.append(f"{row['metric']}: {row['value_cad']:,.2f} ({row['comment']})")

    lines.append("")
    lines.append("things to check")
    if blotter_issues.empty and limit_breaches.empty:
        lines.append("nothing huge from the basic checks")
    else:
        for _, row in blotter_issues.iterrows():
            lines.append(f"blotter - {row['trade_id']}: {row['issue']} ({row['comment']})")
        for _, row in limit_breaches.iterrows():
            lines.append(f"limit - {row['limit_name']}: actual {row['actual']:,.2f}, limit {row['threshold']:,.2f}")

    (OUTPUT_DIR / "desk_pack.txt").write_text("\n".join(lines), encoding="utf-8")
