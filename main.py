
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ccxt
import numpy as np
from datetime import datetime

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

templates = Jinja2Templates(directory="frontends")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Binance
exchange = ccxt.binance({
    "enableRateLimit": True
})

# In-memory strategy equity simulation
equity = [100]  # starting capital

def fetch_prices():
    btc = exchange.fetch_ticker("BTC/USDT")['last']
    eth = exchange.fetch_ticker("ETH/USDT")['last']
    return round(btc, 2), round(eth, 2)

def simulate_equity():
    global equity
    # simple strategy: random walk (replace with your real algo)
    new_value = equity[-1] * (1 + np.random.randn() * 0.001)
    equity.append(round(new_value, 2))
    return equity[-50:]  # last 50 points for chart

@app.get("/crypto")
def crypto_data():
    btc, eth = fetch_prices()
    latest_equity = simulate_equity()
    sharpe = round(np.mean(np.diff(latest_equity)) / (np.std(np.diff(latest_equity)) + 1e-6), 2)
    drawdown = round((min(latest_equity) - max(latest_equity)) / max(latest_equity), 2)

    return {
        "btc": btc,
        "eth": eth,
        "equity": latest_equity,
        "sharpe": sharpe,
        "drawdown": drawdown,
        "time": datetime.now().isoformat()
    }
