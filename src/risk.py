import numpy as np
import pandas as pd

def var_es(losses, level):
    # losses should be positive when losing money
    losses = np.asarray(losses, dtype=float)
    var = np.quantile(losses, level)
    tail = losses[losses >= var]
    es = tail.mean() if len(tail) else var
    return float(var), float(es)


def run_shock_pnl(positions: pd.DataFrame, shocks: pd.DataFrame):
    # simple scenario PnL using DV01 and FX exposure.
    rows = []
    net_dv01 = positions["dv01"].sum()
    net_usd_like = positions.loc[positions["instrument_type"].str.contains("FX", na=False), "fx_exposure_cad"].sum()

    for _, s in shocks.iterrows():
        rate_pnl = -net_dv01 * float(s["cad_rate_shock_bp"])

        # this is rough because we do not split USD/EUR/GBP perfectly in this mini book.
        # still enough to show how a desk pack might think about combined shocks.
        fx_ret_avg = np.mean([float(s["usd_cad_ret"]), float(s["eur_cad_ret"]), float(s["gbp_cad_ret"])])
        fx_pnl = net_usd_like * fx_ret_avg

        total = rate_pnl + fx_pnl
        rows.append({
            "shock_id": s["shock_id"],
            "cad_rate_shock_bp": s["cad_rate_shock_bp"],
            "fx_avg_ret": fx_ret_avg,
            "rate_pnl": rate_pnl,
            "fx_pnl": fx_pnl,
            "total_pnl": total,
            "loss": -total,
            "notes": s["notes"],
        })

    return pd.DataFrame(rows)


def build_risk_summary(positions, shocks):
    scen = run_shock_pnl(positions, shocks)
    losses = scen["loss"].values

    rows = []
    for level in [0.95, 0.99]:
        v, e = var_es(losses, level)
        rows.append({
            "metric": f"VaR {int(level*100)}",
            "value_cad": v,
            "comment": "historical shock file, not a real VaR engine"
        })
        rows.append({
            "metric": f"ES {int(level*100)}",
            "value_cad": e,
            "comment": "average loss past the VaR cut"
        })

    rows.extend([
        {"metric": "Total MTM PnL", "value_cad": positions["mtm_pnl"].sum(), "comment": "sum of row PnL"},
        {"metric": "Net DV01", "value_cad": positions["dv01"].sum(), "comment": "CAD per bp, approximate"},
        {"metric": "Gross Position Value", "value_cad": positions["position_value"].abs().sum(), "comment": "abs market value"},
        {"metric": "Net FX Exposure", "value_cad": positions["fx_exposure_cad"].sum(), "comment": "CAD equivalent"},
    ])

    return pd.DataFrame(rows), scen


def check_limits(positions, risk_summary, limits):
    issues = []
    total_pnl = float(positions["mtm_pnl"].sum())
    net_dv01 = float(positions["dv01"].sum())
    net_fx = float(positions["fx_exposure_cad"].sum())

    var99_row = risk_summary.loc[risk_summary["metric"] == "VaR 99"]
    var99 = float(var99_row["value_cad"].iloc[0]) if not var99_row.empty else 0.0

    get_limit = lambda name: float(limits.loc[limits["limit_name"] == name, "threshold"].iloc[0])

    if abs(net_dv01) > get_limit("CAD_RATES_DV01"):
        issues.append(["CAD_RATES_DV01", net_dv01, get_limit("CAD_RATES_DV01"), "net dv01 is over the simple desk limit"])

    if abs(net_fx) > get_limit("FX_NET_EXPOSURE"):
        issues.append(["FX_NET_EXPOSURE", net_fx, get_limit("FX_NET_EXPOSURE"), "net fx exposure is over the simple desk limit"])

    if total_pnl < get_limit("DAILY_LOSS_LIMIT"):
        issues.append(["DAILY_LOSS_LIMIT", total_pnl, get_limit("DAILY_LOSS_LIMIT"), "daily PnL loss limit hit"])

    if var99 > get_limit("VAR_99_LIMIT"):
        issues.append(["VAR_99_LIMIT", var99, get_limit("VAR_99_LIMIT"), "VaR is above limit"])

    # counterparty check
    cpty = positions.groupby("counterparty", as_index=False)["position_value"].apply(lambda x: x.abs().sum())
    cpty_limit = get_limit("SINGLE_COUNTERPARTY_EXPOSURE")
    for _, row in cpty.iterrows():
        if float(row["position_value"]) > cpty_limit:
            issues.append(["SINGLE_COUNTERPARTY_EXPOSURE", row["position_value"], cpty_limit, f"{row['counterparty']} over cpty exposure limit"])

    return pd.DataFrame(issues, columns=["limit_name", "actual", "threshold", "comment"])
