# StockVision AI

A responsive educational NSE/BSE stock-analysis dashboard.

## Features
- NSE and BSE ticker lookup (for example, RELIANCE on NSE)
- Candlestick chart and volume chart
- Timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1D, 1W, 1M
- Basic candlestick-pattern detection
- Support/resistance snapshots and simple trend/volume heuristics
- Educational technical-bias summary (not investment advice)

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:10000.

## Deploy on Render
Create a Python web service connected to this repository:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Health check path: `/health`
- Runtime: Python 3

No API key is embedded. Market history is retrieved through yfinance/Yahoo Finance and may be delayed, rate-limited, incomplete, or unavailable. Verify data with your broker or exchange. No orders are placed.

## Notes
The chart structures and technical summary are simple heuristics, not a trained AI model or reliable price forecast. Do not use the displayed bias as personalized investment advice.
