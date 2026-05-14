from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from inventory.models import Product


class Forecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecasts', verbose_name=_('Product'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('Created By'))
    period_days = models.IntegerField(default=30, verbose_name=_('Forecast Period (days)'))
    predicted_demand = models.FloatField(verbose_name=_('Predicted Demand'))
    confidence_score = models.FloatField(default=0.0, verbose_name=_('Confidence Score'))
    ai_analysis = models.TextField(blank=True, verbose_name=_('AI Analysis'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Forecast')
        verbose_name_plural = _('Forecasts')
        ordering = ['-created_at']

    def __str__(self):
        return f"Forecast for {self.product.name} - {self.created_at.date()}"


class AIConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    question = models.TextField(verbose_name=_('Question'))
    answer = models.TextField(verbose_name=_('Answer'))
    language = models.CharField(max_length=5, default='en', verbose_name=_('Language'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('AI Conversation')
        verbose_name_plural = _('AI Conversations')
        ordering = ['-created_at']

    def __str__(self):
        return f"Q: {self.question[:50]}..."
