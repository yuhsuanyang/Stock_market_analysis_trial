import os
import time
import json
import requests
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
from django.shortcuts import render

from .models import StockMetaData
# Create your views here.

ROOT = Path(__file__).resolve().parent
today = datetime.today()


def download_punishment(compare_date):
    # 查詢處置股票
    if os.path.exists(f'{ROOT}/punished.csv'):
        modify_time = os.path.getmtime(f'{ROOT}/punished.csv')
        modify_time = time.strftime('%Y%m%d', time.localtime(modify_time))
        if modify_time == compare_date:  #這天已經查過 不用再查了
            return
    else:
        modify_time = compare_date
        print(modify_time)


#        modify_time = datetime.strptime(modify_time, '%Y%m%d')
    end = datetime.strptime(compare_date, '%Y%m%d') + timedelta(days=1)
    end = datetime.strftime(end, '%Y%m%d')

    r = requests.post(
        f'https://www.twse.com.tw/announcement/punish?response=json&startDate={modify_time}&endDate={end}'
    )
    df = pd.DataFrame(json.loads(r.text)['data'])[[2, 6]]
    df.columns = ['code', 'duration']
    df.to_csv(f'{ROOT}/punished.csv', index=False)


def get_latest_data():  # 即時爬取大盤資料
    start_date = datetime.strftime(today - timedelta(days=10), '%Y-%m-%d')
    end_date = datetime.strftime(today + timedelta(days=1), '%Y-%m-%d')
    print(start_date)
    print(end_date)
    data = yf.download("^TWII", start=start_date, end=end_date)
    data['Date'] = data.index.astype(str)
    data = data.reset_index(drop=True)
    print(data)
    return {
        'date': data['Date'].iloc[-1],
        'yesterday_close': round(data['Close'].iloc[-2], 2),
        'today_close': round(data['Close'].iloc[-1], 2),
        'low': round(data['Low'].iloc[-1], 2),
        'high': round(data['High'].iloc[-1], 2),
        'open': round(data['Open'].iloc[1], 2)
    }


def main(request):
    meta_data = StockMetaData.objects.all()
    stocks = [stock.__str__() for stock in meta_data]
    data = get_latest_data()
    download_punishment(today.strftime('%Y%m%d'))
    if data['today_close'] > data['yesterday_close']:
        trend_light = 'pink'
        trend = 'red'
    elif data['today_close'] < data['yesterday_close']:
        trend_light = 'lightgreen'
        trend = 'green'
    else:
        trend_light = 'lightgrey'
        trend = 'gold'
    data['trend'] = trend
    data['trend_background'] = trend_light
    print('-' * 20)
    print(data)
    data['stock_list'] = stocks
    return render(request, 'index.html', context=data)
