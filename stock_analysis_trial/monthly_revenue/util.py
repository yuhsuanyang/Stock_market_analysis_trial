import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from price.views import query_historical_price

from datetime import datetime
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots
from django_plotly_dash import DjangoDash
from dashboard_utils.common_styles import layout_style
from dashboard_utils.common_functions import plot_table


def query_month_avg_price(stock_code, start_month, end_month):
    start_date = datetime.strptime(start_month, '%Y-%m')
    end_date = datetime.strptime(end_month, '%Y-%m') + relativedelta(months=1)
    start_date = datetime.strftime(start_date, '%Y-%m-%d')
    end_date = datetime.strftime(end_date, '%Y-%m-%d')
    data = query_historical_price(stock_code, start_date,
                                  end_date)[['date', 'close']]
    #    print(data)
    data['month'] = data['date'].apply(lambda x: x[:7])
    return data.groupby(['month']).mean()


def create_dash(data):
    app = DjangoDash('MonthlyRevenue_Dashboard')
    stock_code = data['stock_id'].values[0]
    df = data.drop(columns=['stock_id'])
    df = df.rename(
        columns={
            'revenue_year': '年',
            'revenue_month': '月',
            'revenue': '月營收',
            'month_increment': '月增率%',
            'year_increment': '年增率%'
        })
    data['年月'] = df['年'].astype(str) + '_' + df['月'].astype(str)
    years = sorted(df['年'].unique())
    start_month = f"{df['年'].iloc[0]}-{df['月'].iloc[0]}"
    end_month = f"{df['年'].iloc[-1]}-{df['月'].iloc[-1]}"
    month_avg_price = query_month_avg_price(stock_code, start_month, end_month)
    table = plot_table(df)

    fig_bar = make_subplots(specs=[[{"secondary_y": True}]])
    fig_bar.add_trace(
        go.Bar(x=data['年月'], y=data['revenue'].values, name='月營收',
               opacity=0.5))
    fig_bar.add_trace(go.Scatter(x=data['年月'],
                                 y=month_avg_price['close'].values,
                                 name='月均收盤價'),
                      secondary_y=True)

    fig_bar.update_layout(
        xaxis={
            'tickmode': 'array',
            'tickvals': [i * 12 for i in range(len(years))],
            'ticktext': [f"{year}_1" for year in years]
        })
    app.layout = html.Div([
        html.H3(children='月營收表', style={'text_align': 'center'}),
        dcc.Graph(id='bar_chart',
                  figure=fig_bar,
                  style={
                      'marginLeft': '5%',
                      'width': '90%',
                      'text-align': 'center'
                  }),
        html.Div(
            [html.P(children='單位: 千元', style={'marginLeft': '90%'}), table],
            style={
                'marginRight': '10%',
                'marginLeft': '10%',
                'width': '80%',
            }),
    ],
                          style=layout_style)
