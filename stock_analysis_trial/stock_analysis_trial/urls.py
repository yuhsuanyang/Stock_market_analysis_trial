"""stock_analysis_trial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from stocks.views import main

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', main, name='index'),
    path(
        'css/styles.css',
        TemplateView.as_view(template_name='styles.css',
                             content_type='text/css'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
