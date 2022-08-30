import pandas as pd
from pathlib import Path
from FinMind.data import DataLoader
from datetime import datetime, timedelta
from django.urls import reverse
from django.shortcuts import render, redirect
from stocks.models import StockMetaData
from .util import create_dash
# Create your views here.
api = DataLoader()

root = Path(__file__).resolve().parent.parent  # ../stock_analysis_trial
meta_data = StockMetaData.objects.all()
stock_code = ''
punished = pd.read_csv(f'{root}/stocks/punished.csv')


def get_posted_query(request):
    stock_id = request.POST['stock_id'].split(' ')[0]
    return redirect(reverse('price:dashboard', kwargs={'stock_id': stock_id}))


def color(price1, price2):  #price2: 昨收
    #return: background_color, font_color
    if price1 > price2:
        if (price1 - price2) / price2 >= 0.095:
            return 'red', 'white'
        else:
            return 'white', 'red'
    elif price1 < price2:
        if (price1 - price2) / price2 <= -0.095:
            return 'green', 'white'
        else:
            return 'white', 'green'
    else:
        return 'white', 'black'


def query_historical_price(stock_code, start_date, end_date):
    df_price = api.taiwan_stock_daily(stock_code, start_date, end_date)[[
        'date', 'open', 'max', 'min', 'close', 'Trading_Volume'
    ]]
    df_per = api.taiwan_stock_per_pbr(stock_code, start_date,
                                      end_date)[['date', 'PER']]
    df = df_price.merge(df_per)
    print(df)
    return df


def main(request, stock_id):
    data = {}
    info = meta_data.filter(code=stock_id)[0]
    today = datetime.today()
    start_date = datetime.strftime(today - timedelta(days=365 * 5), '%Y-%m-%d')
    end_date = datetime.strftime(today + timedelta(days=1), '%Y-%m-%d')
    same_trade = meta_data.filter(industry_type=info.industry_type)
    price_df = query_historical_price(stock_id, start_date, end_date)
    price_df['5MA'] = price_df['close'].rolling(5).mean()
    price_df['20MA'] = price_df['close'].rolling(20).mean()
    price_df['60MA'] = price_df['close'].rolling(60).mean()

    if int(stock_id) in punished['code'].values:
        duration = punished[punished.code == int(
            stock_id)]['duration'].values[0].split('～')
        data['punishment_duration'] = duration[0][4:] + '~' + duration[1][4:]

    data['previous_close'] = price_df.iloc[-2]['close']
    data['today_date'] = price_df.iloc[-1]['date']
    for col in ['open', 'max', 'min', 'close']:
        data[col] = price_df.iloc[-1][col]
        data[f'{col}_highlight_color'], data[f'{col}_color'] = color(
            data[col], data['previous_close'])
    data['PER'] = price_df.iloc[-1]['PER']
    data['volume'] = price_df.iloc[-1]['Trading_Volume'] / 100
    data['updown'] = round(data['close'] - data['previous_close'], 2)
    data['amplitude'] = round(data['updown'] * 100 / data['previous_close'], 2)
    data['updown_color'] = [
        c for c in [data['close_color'], data['close_highlight_color']]
        if c != 'white'
    ][0]
    data['stock_id'] = f"{stock_id} {info.name}"
    data['stock_info'] = info
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['market_type'] = info.market_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    app = create_dash(
        stock_id, info.name,
        price_df.rename(columns={
            'close': 'daily',
            'Trading_Volume': 'volume'
        }))
    return render(request, 'price_dashboard.html', context=data)
