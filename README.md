# InvStock - Order Forecasting & Inventory Management

A Django web application for managing inventory and forecasting orders with AI assistance.

## Quick Start

### 1. Setup Python environment
```bash
# Requires Python 3.12.9 (see .python-version)
pip install -r requirements.txt
```

### 2. Configure OpenRouter API Key
Edit `inventory_project/settings.py`:
```python
OPENROUTER_API_KEY = 'your-actual-openrouter-api-key'
```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Seed the database
```bash
python manage.py seed
```

### 5. Start the server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

## Default Credentials
- **Admin**: `admin` / `admin123`
- **Demo User**: `demo` / `demo123`
- **Admin Panel**: http://localhost:8000/admin/

## Features
- 📦 Product & inventory management with low-stock alerts
- 🛒 Order tracking (purchase & sales)
- 🚚 Supplier management
- 📊 Stock movement history
- 🤖 AI-powered demand forecasting (via OpenRouter)
- 💬 AI chat assistant for inventory insights
- 🌐 Multi-language: English, Russian, Uzbek
- 🎨 Professional dark admin panel (Jazzmin + Flatly theme)

## Languages
Switch between **UZ / RU / EN** using the buttons in the top navigation bar.
All AI responses adapt to the selected language.
