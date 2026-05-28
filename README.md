# Mock CAD Rates, FX, and Trading-Book Pricing Prototype

This is a student project I built to practise the kind of basic pricing, PnL, and risk work that might sit around a rates / FX desk.

It is **not** a real trading system. It uses fake trades and fake market data. I made it more like a small desk support tool: trade inputs go in, the script checks the blotter, prices positions, looks at PnL, compares dealer quotes, and writes some simple reports.

I made this because I wanted something more practical than just writing about fixed income or liquidity risk. This repo is basically me trying to connect the concepts from actuarial / financial math coursework to a mock front-office workflow.

## What it does

The project covers a small mock book with:

- Government of Canada style bonds
- CAD FX spot and forwards
- simple interest-rate swaps
- bond forwards
- interest-rate futures

The script produces:

- trade blotter checks
- position valuation
- realised / unrealised style PnL, simplified
- DV01, duration, convexity
- FX exposure
- VaR and Expected Shortfall from a small shock file
- dealer quote comparison
- stale / missing / duplicate trade flags
- basic desk report CSVs

## Why this is still a mock project

A real desk would have proper market data feeds, curves, confirmations, settlement systems, risk engines, approvals, and a lot more controls. I obviously do not have that here.

So I kept this as a clean student version:

- mock trade data
- manually supplied market data
- simple curve interpolation
- simplified swap PV logic
- simplified bond forward pricing
- no live market data
- no actual execution

Still, the point is to show that I understand the workflow pieces: trade data, pricing inputs, risk numbers, quote comparison, and daily reporting.

## Repo layout

```text
data/
  trades_mock.csv              mock trade blotter
  market_rates.csv             yield / FX / futures / forward inputs
  dealer_quotes.csv            fake dealer quotes for comparison
  historical_shocks.csv        mock market shocks for VaR / ES
  risk_limits.csv              simple mock limits

src/
  main.py                      runs the whole project
  loader.py                    loads CSV files
  checks.py                    blotter checks and data issues
  pricing.py                   bond / FX / swap / future pricing helpers
  risk.py                      DV01, VaR, ES, limit checks
  reports.py                   writes CSV reports
  config.py                    valuation date and file paths

excel/
  vba_refresh_report.bas       rough VBA macro to refresh CSV outputs in Excel
  workbook_notes.md            how I would wire this into an Excel workbook

docs/
  model_notes.md               notes on assumptions and limitations
  resume_bullet_version.md     resume bullets based on the repo

outputs/
  reports get written here after running the script
```

## How to run it

Install the small set of packages:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python src/main.py
```

The reports will show up in `outputs/`.

## Main outputs

After running it, the main files are:

- `outputs/blotter_issues.csv`
- `outputs/position_report.csv`
- `outputs/pnl_report.csv`
- `outputs/risk_summary.csv`
- `outputs/dealer_quote_comparison.csv`
- `outputs/limit_breaches.csv`
- `outputs/desk_pack.txt`

## Notes on the modelling

I am not claiming the pricing is institutional-grade.

For bonds, I use basic discounted cash flow pricing and calculate duration / convexity from cash flows.

For FX spot and forwards, I use the supplied rates and forward points. I am not building a full cross-currency curve here.

For swaps, I use a simplified fixed-vs-floating approximation from a flat/interpolated curve rate. It is enough for a mock project, but not how a real swap book would be priced.

For VaR and ES, I use a simple historical shock file. Again, not perfect, but useful for showing how the risk report could work.

## Resume version

The clean resume wording for this project would be:

> Built a simulated CAD rates, FX, and trading-book pricing prototype using mock trade data, covering Government of Canada bonds, FX spot/forwards, interest-rate swaps, bond forwards, and futures.

> Calculated mark-to-market PnL, DV01, duration, convexity, FX exposure, VaR, Expected Shortfall, and risk-limit usage across a mock front-office book.

> Built dealer quote comparison and blotter-control checks to flag stale prices, missing inputs, duplicate trade IDs, off-market quotes, and limit breaches before report output.

## Disclaimer

This repo is for learning and job-application evidence only. It is not investment advice, not a trading system, and not connected to any real bank or trading desk.
