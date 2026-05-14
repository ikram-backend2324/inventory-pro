import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.utils.translation import get_language
from inventory.models import Product, Order, StockMovement
from .models import Forecast, AIConversation


def get_inventory_context():
    products = Product.objects.select_related('category').all()
    context_lines = []
    for p in products[:20]:
        context_lines.append(
            f"- {p.name} (SKU: {p.sku}): stock={p.quantity_in_stock}, reorder_level={p.reorder_level}, price={p.unit_price}"
        )
    orders = Order.objects.all()[:10]
    order_lines = [f"- Order #{o.order_number}: {o.order_type}, status={o.status}, amount={o.total_amount}" for o in orders]
    return "\n".join(context_lines), "\n".join(order_lines)


LANGUAGE_INSTRUCTIONS = {
    'en': "Please respond in English.",
    'ru': "Пожалуйста, отвечайте на русском языке.",
    'uz': "Iltimos, o'zbek tilida javob bering.",
}


@login_required
def forecast_list(request):
    forecasts = Forecast.objects.select_related('product', 'created_by').all()[:20]
    products = Product.objects.all()
    return render(request, 'forecasting/forecast_list.html', {
        'forecasts': forecasts,
        'products': products,
    })


@login_required
def ai_assistant(request):
    conversations = AIConversation.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'forecasting/ai_assistant.html', {
        'conversations': conversations,
    })


@login_required
def ai_ask(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        lang = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else get_language() or 'en'
        lang = lang[:2]
        lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS['en'])

        products_ctx, orders_ctx = get_inventory_context()

        system_prompt = f"""You are an AI assistant specializing in inventory management and order forecasting.
You have access to the following inventory data:

PRODUCTS:
{products_ctx}

RECENT ORDERS:
{orders_ctx}

Your role is to:
1. Analyze inventory levels and predict future demand
2. Recommend reorder points and quantities
3. Identify slow-moving or fast-moving products
4. Provide actionable insights for inventory optimization

{lang_instruction}
Be concise, practical, and data-driven in your responses."""

        api_key = settings.OPENROUTER_API_KEY
        response = requests.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Inventory Management System",
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                "max_tokens": 800,
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']

            AIConversation.objects.create(
                user=request.user,
                question=question,
                answer=answer,
                language=lang,
            )

            return JsonResponse({'answer': answer})
        else:
            return JsonResponse({'error': f'API error: {response.status_code} - {response.text}'}, status=500)

    except requests.Timeout:
        return JsonResponse({'error': 'Request timed out. Please try again.'}, status=504)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def generate_forecast(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        period = int(data.get('period', 30))

        product = Product.objects.get(pk=product_id)
        lang = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else get_language() or 'en'
        lang = lang[:2]
        lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS['en'])

        movements = StockMovement.objects.filter(product=product).order_by('-created_at')[:30]
        movement_summary = "\n".join([f"- {m.movement_type}: {m.quantity} on {m.created_at.date()}" for m in movements])

        prompt = f"""Analyze the following product and provide a demand forecast for the next {period} days.

Product: {product.name} (SKU: {product.sku})
Current Stock: {product.quantity_in_stock}
Reorder Level: {product.reorder_level}
Reorder Quantity: {product.reorder_quantity}
Unit Price: {product.unit_price}

Recent Stock Movements:
{movement_summary if movement_summary else 'No recent movements'}

Please provide:
1. Estimated demand for next {period} days (a single number)
2. Confidence level (0-100%)
3. Key factors affecting demand
4. Recommendation (reorder now / monitor / sufficient stock)

{lang_instruction}
Format your response as JSON with keys: predicted_demand (number), confidence (number 0-100), analysis (text), recommendation (text)"""

        api_key = settings.OPENROUTER_API_KEY
        response = requests.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Inventory Forecasting",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            try:
                forecast_data = json.loads(content)
            except Exception:
                forecast_data = {"predicted_demand": 0, "confidence": 50, "analysis": content, "recommendation": ""}

            forecast = Forecast.objects.create(
                product=product,
                created_by=request.user,
                period_days=period,
                predicted_demand=forecast_data.get('predicted_demand', 0),
                confidence_score=forecast_data.get('confidence', 50) / 100,
                ai_analysis=forecast_data.get('analysis', '') + "\n\nRecommendation: " + forecast_data.get('recommendation', ''),
            )
            return JsonResponse({
                'success': True,
                'forecast_id': forecast.id,
                'predicted_demand': forecast.predicted_demand,
                'confidence': forecast_data.get('confidence', 50),
                'analysis': forecast.ai_analysis,
            })
        else:
            return JsonResponse({'error': f'API error: {response.status_code}'}, status=500)

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
