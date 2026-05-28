from loader import load_inputs
from checks import check_trade_blotter, check_quotes
from pricing import build_position_report
from risk import build_risk_summary, check_limits
from reports import compare_dealer_quotes, write_outputs

def main():
    trades, market, quotes, shocks, limits = load_inputs()

    blotter_issues = check_trade_blotter(trades)
    quote_issues = check_quotes(quotes)
    all_issues = __import__("pandas").concat([blotter_issues, quote_issues], ignore_index=True)

    position_report = build_position_report(trades, market)
    quote_report = compare_dealer_quotes(trades, quotes)
    risk_summary, shock_report = build_risk_summary(position_report, shocks)
    limit_breaches = check_limits(position_report, risk_summary, limits)

    write_outputs(all_issues, position_report, quote_report, risk_summary, shock_report, limit_breaches)

    print("done - check the outputs folder")
    print(f"trades priced: {len(position_report)}")
    print(f"total pnl: {position_report['mtm_pnl'].sum():,.2f}")
    print(f"issues found: {len(all_issues) + len(limit_breaches)}")

if __name__ == "__main__":
    main()
