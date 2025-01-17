from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from database.database import DataBase,User,Stock, EmailRequest
from api import email
from datetime import datetime
import json
import pytz
import uvicorn
import yfinance as yf

from yFinanceTempFix.yfFix import YFinance
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

app.include_router(email.router)

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "http://localhost",
    "http://stockwatch.cloud",
    "http://www.stockwatch.cloud",
    "https://stockwatch.cloud",
    "https://www.stockwatch.cloud"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
scheduler = BackgroundScheduler()
scheduler.start()

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(update_stock_prices, "interval", hours=1)


@app.post("/insertList")
async def insert_user(user:User):
    obj = DataBase()
    #Convert to dict
    jsonUser = user.model_dump()
    obj.insert_user_data(jsonUser)
    print(jsonUser)
    return jsonUser

@app.get("/getUserSetStockValues")
async def get_stock_threshold_values(emailrequest : EmailRequest):
    obj = DataBase()
    email = emailrequest.email
    return obj.get_user_data(email)

@app.get("/stockList/{stockName}")
def get_stock_info(stockName: str):
    stock = YFinance(stockName)
    return stock.info

@app.get("/stocklistDB")
def get_list():
    obj = DataBase()
    return obj.get_stocks()

@app.get("/stock/{stockName}")
def filter(stockName: str):
    wholeStockInfo = yf.Ticker(stockName)
    
    shortName = wholeStockInfo.info["shortName"]
    currentPrice = float(wholeStockInfo.info["currentPrice"])
    est_timezone = pytz.timezone('US/Eastern')
    current_time = str(datetime.datetime.now().time())
    current_date = str(datetime.date.today())
    
    my_json_string = json.dumps({'stockName': stockName, 'shortName': shortName, 'currentPrice': currentPrice, 'currentDate': current_date, 'currentTime': current_time})
    my_json = json.loads(my_json_string)
    return my_json

def update_stock_prices():
    
    print(f"Updating stock prices at {datetime.now()}")
    stock_tickers = ["AAPL", "GOOG", "MSFT"]  

    for ticker in stock_tickers:
        yfinance_instance = YFinance(ticker)
        stock_info = yfinance_instance.info

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)