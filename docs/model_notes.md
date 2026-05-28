# Model notes

These are the assumptions I used. Mostly writing this down so the project does not look like it is pretending to be more than it is.

## Bonds

The bond pricing is basic discounted cash flow pricing.

Inputs used:

- face value
- coupon rate
- maturity
- yield
- semi-annual coupons

Outputs:

- price
- modified duration
- convexity
- DV01

This is fine for a student project. A real desk would care more about the exact bond, accrued interest, day count, settlement date, curve construction, repo/funding, and pricing source.

## FX

FX spot and forwards are marked using the trade rate, current spot, and a forward points input.

This is not a full FX forward curve. I kept it simple because the point of this repo is the workflow.

## Swaps

The swap value is a rough fixed-vs-floating approximation.

I use an interpolated CAD curve rate as a simple par rate, then value the fixed-rate difference over an annuity.

A real swap book would need full discount and projection curves, payment dates, compounding conventions, collateral discounting, calendars, and so on.

## VaR and Expected Shortfall

The VaR and ES are based on the mock shock file in `data/historical_shocks.csv`.

That file has rate shocks and FX returns. The code applies a rough combined shock to the position report.

Not perfect, but it shows the reporting workflow:

- build position report
- calculate approximate exposures
- apply shocks
- estimate tail loss
- compare to limits

## Limits

The risk limits are just simple demo limits.

They check:

- net DV01
- net FX exposure
- daily loss
- VaR 99
- single counterparty exposure

## What I would improve next

- split FX exposure by currency pair instead of using an average return
- add actual bond identifiers
- add accrued interest
- add settlement dates
- add a better swap schedule
- add charts in Excel
- add a cleaner PnL explain by rate move vs FX move
