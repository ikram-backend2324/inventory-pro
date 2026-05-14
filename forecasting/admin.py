from django.contrib import admin
from .models import Forecast, AIConversation


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ['product', 'period_days', 'predicted_demand', 'confidence_score', 'created_by', 'created_at']
    list_filter = ['period_days']
    search_fields = ['product__name']


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'language', 'created_at']
    list_filter = ['language']
    search_fields = ['question', 'user__username']
