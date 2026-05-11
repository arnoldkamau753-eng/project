from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import random
import datetime
import numpy as np

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# MARKET CONFIG
# =========================
SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY",
    "XAUUSD", "XAGUSD",
    "BTCUSD"
]

# =========================
# MARKET SESSION DETECTION
# =========================
def get_session():
    hour = datetime.datetime.utcnow().hour

    if 0 <= hour < 8:
        return "Asia"
    elif 8 <= hour < 16:
        return "London"
    else:
        return "New York"

def is_market_open(symbol):
    now = datetime.datetime.utcnow()
    weekday = now.weekday()

    if symbol == "BTCUSD":
        return True

    if weekday >= 5:
        return False

    return True

# =========================
# INDICATORS
# =========================
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    gain = np.maximum(deltas, 0).mean()
    loss = -np.minimum(deltas, 0).mean()
    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period=10):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return np.convolve(prices, weights, mode='valid')[-1]

# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(symbol):
    if not is_market_open(symbol):
        return {"symbol": symbol, "status": "closed"}

    prices = np.random.normal(100, 1, 50)

    rsi = calculate_rsi(prices)
    ema_fast = calculate_ema(prices, 5)
    ema_slow = calculate_ema(prices, 20)

    trend = "up" if ema_fast > ema_slow else "down"

    confidence = random.randint(60, 95)

    if confidence < 70:
        return None

    if trend == "up" and rsi < 70:
        signal = "Strong Buy" if confidence > 85 else "Buy"
    elif trend == "down" and rsi > 30:
        signal = "Strong Sell" if confidence > 85 else "Sell"
    else:
        signal = "Neutral"

    price = round(prices[-1], 5)

    return {
        "symbol": symbol,
        "signal": signal,
        "price": price,
        "confidence": confidence,
        "time": str(datetime.datetime.utcnow()),
        "sl": round(price - 0.002, 5),
        "tp": round(price + 0.004, 5),
        "session": get_session()
    }

# =========================
# ROUTES
# =========================
@app.get("/")
async def home():
    with open("templates/dashboard.html") as f:
        return HTMLResponse(f.read())

# =========================
# WEBSOCKET
# =========================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = []

        for symbol in SYMBOLS:
            signal = generate_signal(symbol)
            if signal:
                data.append(signal)

        await websocket.send_json(data)

        await asyncio.sleep(2)