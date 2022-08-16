import pandas as pd
from pathlib import Path
from .models import StockMetaData

ROOT = Path(__file__).resolve().parent
print(ROOT)
stock_codes = pd.read_csv(f'{ROOT}/stock_codes.csv')
column_names = stock_codes.columns


# column_names = ['有價證券代號及名稱', '上市日', '市場別', '產業別']
def add_stocks():
    for i in range(len(stock_codes)):
        names = stock_codes.iloc[i][column_names[0]].replace('\u3000',
                                                             ' ').split(' ')
        row = StockMetaData(code=names[0],
                            name=names[1],
                            listed_date=stock_codes.iloc[i][column_names[1]],
                            market_type=stock_codes.iloc[i][column_names[2]],
                            industry_type=stock_codes.iloc[i][column_names[3]])
        row.save()
        print(names, 'successfully added')
