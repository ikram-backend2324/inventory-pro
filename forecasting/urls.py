from django.urls import path
from . import views

app_name = 'forecasting'

urlpatterns = [
    path('', views.forecast_list, name='forecast_list'),
    path('ai/', views.ai_assistant, name='ai_assistant'),
    path('ai/ask/', views.ai_ask, name='ai_ask'),
    path('generate/', views.generate_forecast, name='generate_forecast'),
]
