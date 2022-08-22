import pandas as pd
from pathlib import Path
from FinMind.data import DataLoader
from django.shortcuts import render, redirect
from stocks.models import StockMetaData

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
    same_trade = meta_data.filter(industry_type=info.industry_type)
    data['stock_id'] = f"{stock_id} {info.name}"
    data['stock_info'] = info
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['market_type'] = info.market_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    return render(request, 'price_dashboard.html', context=data)
