import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.shortcuts import render
from FinMind.data import DataLoader
from stocks.models import StockMetaData
from .util import create_dash

# Create your views here.
meta_data = StockMetaData.objects.all()
api = DataLoader()


def get_revenue(stock_id, start):
    first_year = int(start.split('-')[0])
    raw_data = api.taiwan_stock_month_revenue(stock_id, start)
    raw_data = raw_data[[
        'stock_id', 'revenue_year', 'revenue_month', 'revenue'
    ]]
    raw_data['month_increment'] = raw_data['revenue'].diff()
    raw_data[
        'month_increment'] = raw_data['month_increment'] / raw_data['revenue']

    year_increment = []
    for i in range(len(raw_data)):
        year = raw_data.iloc[i]['revenue_year']
        month = raw_data.iloc[i]['revenue_month']
        revenue = raw_data.iloc[i]['revenue']
        if year == first_year:
            year_increment.append(np.nan)
        else:
            last_year_same_month = raw_data[
                (raw_data['revenue_year'] == year - 1)
                & (raw_data['revenue_month'] == month)].iloc[0]
            year_increment.append(
                (revenue - last_year_same_month['revenue']) / revenue)
    raw_data['year_increment'] = pd.DataFrame(year_increment)
    raw_data.dropna(inplace=True)
    raw_data['month_increment'] = raw_data['month_increment'].apply(
        lambda x: round(x * 100, 2))
    raw_data['year_increment'] = raw_data['year_increment'].apply(
        lambda x: round(x * 100, 2))
    return raw_data


def main(request, stock_id):
    today = datetime.today()
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    df = get_revenue(
        stock_id,
        datetime.strftime(today - timedelta(days=6 * 365), '%Y') + '-01-01')
    app = create_dash(df)
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['stock_info'] = info
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    return render(request, 'monthly_revenue_dashboard.html', context=data)
