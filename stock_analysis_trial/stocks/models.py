from django.db import models
from django.urls import reverse


# Create your models here.
class StockMetaData(models.Model):
    code = models.CharField(max_length=4, primary_key=True, help_text='公司代碼')
    name = models.CharField(max_length=10, help_text='公司名稱')
    listed_date = models.CharField(max_length=10, help_text='上市日期')
    industry_type = models.CharField(max_length=20, help_text='產業類別')
    market_type = models.CharField(max_length=20, help_text='市場類別')

    def __str__(self):
        return f"{self.code} {self.name}"

    @staticmethod
    def get_columns():
        return {
            'code': '公司代碼',
            'name': '公司名稱',
            'listed_date': '上市日期',
            'industry_type': '產業類別',
            'market_type': '市場類別',
        }

    def get_price_url(self):
        return reverse('price:dashboard', args=[self.code])
