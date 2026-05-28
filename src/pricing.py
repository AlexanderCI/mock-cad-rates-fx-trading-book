import numpy as np
import pandas as pd

def sign_for_side(side: str) -> int:
    if side in ["BUY", "RECEIVE_FIXED"]:
        return 1
    if side in ["SELL", "PAY_FIXED"]:
        return -1
    return 1


def interp_rate(market: pd.DataFrame, tenor: float, col: str = "cad_zero_rate") -> float:
    # simple linear interpolation. good enough for this project.
    x = market["curve_tenor_years"].astype(float).values
    y = market[col].astype(float).values
    return float(np.interp(float(tenor), x, y))


def bond_cashflows(face: float, coupon_rate: float, maturity_years: float, freq: int = 2):
    n = int(round(maturity_years * freq))
    coupon = face * coupon_rate / freq
    times = np.arange(1, n + 1) / freq
    cfs = np.full(n, coupon)
    cfs[-1] += face
    return times, cfs


def bond_price_duration_convexity(face, coupon_rate, ytm, maturity_years, freq=2):
    # basic clean-ish price from discounted cash flows.
    if maturity_years <= 0:
        return 100.0, 0.0, 0.0

    times, cfs = bond_cashflows(face, coupon_rate, maturity_years, freq)
    per_period_y = ytm / freq
    periods = np.arange(1, len(cfs) + 1)
    dfs = 1 / ((1 + per_period_y) ** periods)
    pv = cfs * dfs
    price_value = pv.sum()
    price_per_100 = price_value / face * 100

    weights = pv / price_value
    macaulay_duration = np.sum(weights * times)
    modified_duration = macaulay_duration / (1 + ytm / freq)

    # a plain convexity approximation. not trying to win a quant prize here.
    convexity = np.sum(pv * times * (times + 1 / freq)) / (price_value * (1 + ytm / freq) ** 2)
    return float(price_per_100), float(modified_duration), float(convexity)


def swap_value(row, market):
    notional = float(row["notional"])
    fixed_rate = float(row["fixed_rate"])
    tenor = float(row["curve_tenor_years"])
    par_rate = interp_rate(market, tenor, "cad_zero_rate")

    # very simplified annuity. real swap pricing would use a full curve.
    if par_rate == 0:
        annuity = tenor
    else:
        annuity = (1 - (1 + par_rate) ** (-tenor)) / par_rate

    receive_fixed_value = notional * (fixed_rate - par_rate) * annuity
    if row["side"] == "PAY_FIXED":
        receive_fixed_value *= -1

    dv01 = notional * annuity * 0.0001
    if row["side"] == "PAY_FIXED":
        dv01 *= -1

    return receive_fixed_value, dv01, par_rate


def fx_forward_rate(spot, fwd_points):
    # for these pairs, points are in 1/10000. kept simple.
    return float(spot) + float(fwd_points) / 10000


def price_trade(row, market):
    typ = row["instrument_type"]
    side = sign_for_side(row["side"])

    out = {
        "trade_id": row["trade_id"],
        "instrument_type": typ,
        "book": row["book"],
        "counterparty": row["counterparty"],
        "currency": row["currency"],
        "position_value": 0.0,
        "initial_value": 0.0,
        "mtm_pnl": 0.0,
        "dv01": 0.0,
        "duration": 0.0,
        "convexity": 0.0,
        "fx_exposure_cad": 0.0,
        "pricing_note": "",
    }

    if typ == "GOC_BOND":
        face = float(row["quantity"])
        coupon = float(row["coupon_rate"])
        maturity = float(row["maturity_years"])
        current_yield = float(row["current_yield"])
        calc_price, duration, convexity = bond_price_duration_convexity(face, coupon, current_yield, maturity)

        current_price = float(row["current_price"])
        trade_price = float(row["trade_price"])

        out["position_value"] = side * face * current_price / 100
        out["initial_value"] = side * face * trade_price / 100
        out["mtm_pnl"] = side * face * (current_price - trade_price) / 100
        out["duration"] = duration
        out["convexity"] = convexity
        out["dv01"] = side * duration * (face * current_price / 100) * 0.0001
        out["pricing_note"] = f"bond calc px {calc_price:.3f}, used blotter px {current_price:.3f}"

    elif typ == "FX_SPOT":
        notional = float(row["notional"])
        trade_fx = float(row["trade_fx_rate"])
        current_fx = float(row["current_fx_rate"])
        out["position_value"] = side * notional * current_fx
        out["initial_value"] = side * notional * trade_fx
        out["mtm_pnl"] = side * notional * (current_fx - trade_fx)
        out["fx_exposure_cad"] = side * notional * current_fx
        out["pricing_note"] = "spot fx reval"

    elif typ == "FX_FORWARD":
        notional = float(row["notional"])
        trade_fx = float(row["trade_fx_rate"])
        current_fx = float(row["current_fx_rate"])
        fwd = fx_forward_rate(current_fx, float(row["forward_points"]))
        out["position_value"] = side * notional * fwd
        out["initial_value"] = side * notional * trade_fx
        out["mtm_pnl"] = side * notional * (fwd - trade_fx)
        out["fx_exposure_cad"] = side * notional * fwd
        out["pricing_note"] = f"forward rate {fwd:.5f}"

    elif typ == "IRS":
        pv, dv01, par_rate = swap_value(row, market)
        out["position_value"] = pv
        out["initial_value"] = 0.0
        out["mtm_pnl"] = pv
        out["dv01"] = dv01
        out["pricing_note"] = f"simplified swap pv vs par {par_rate:.4%}"

    elif typ == "BOND_FORWARD":
        face = float(row["quantity"])
        coupon = float(row["coupon_rate"])
        maturity = float(row["maturity_years"])
        current_yield = float(row["current_yield"])
        funding_rate = interp_rate(market, float(row["curve_tenor_years"]), "funding_rate")
        spot_price, duration, convexity = bond_price_duration_convexity(face, coupon, current_yield, maturity)

        # rough 3 month forward. ignores accrued interest on purpose.
        theoretical_forward = spot_price * (1 + funding_rate * 0.25)
        contract_price = float(row["contract_price"])

        out["position_value"] = side * face * theoretical_forward / 100
        out["initial_value"] = side * face * contract_price / 100
        out["mtm_pnl"] = side * face * (theoretical_forward - contract_price) / 100
        out["duration"] = duration
        out["convexity"] = convexity
        out["dv01"] = side * duration * (face * spot_price / 100) * 0.0001
        out["pricing_note"] = f"rough fwd px {theoretical_forward:.3f}"

    elif typ == "IR_FUTURE":
        notional = float(row["notional"])
        qty = float(row["quantity"])
        trade_px = float(row["futures_price"])
        current_px = float(market.loc[market["curve_tenor_years"] == 0.25, "cad_futures_price"].iloc[0])
        tick_value = notional / 100
        out["position_value"] = side * qty * current_px * tick_value
        out["initial_value"] = side * qty * trade_px * tick_value
        out["mtm_pnl"] = side * qty * (current_px - trade_px) * tick_value
        out["dv01"] = side * qty * 25  # rough placeholder
        out["pricing_note"] = "simple futures reval"

    return out


def build_position_report(trades, market):
    rows = []
    for _, row in trades.iterrows():
        rows.append(price_trade(row, market))
    return pd.DataFrame(rows)
