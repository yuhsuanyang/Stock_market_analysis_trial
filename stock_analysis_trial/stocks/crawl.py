import requests
import pandas as pd

listed_url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
over_counter_url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'


def crawl(url):
    r = requests.get(url)
    df = pd.read_html(r.text)[0]
    df.columns = df.iloc[0]
    df = df.drop(0)
    return df


listed = crawl(listed_url)
over_counter = crawl(over_counter_url)
df = pd.concat([listed, over_counter], ignore_index=True)
df = df.drop(columns=['國際證券辨識號碼(ISIN Code)', '備註'])
df = df[df['有價證券代號及名稱'].str.match('^([0-9])')]
df.dropna(inplace=True)
df.to_csv('stock_codes.csv', index=False)
print(df.shape)
