import json
import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Инициализация временных файлов БД в формате JSON
ORDERS_FILE = 'orders.json'
BONUS_FILE = 'bonus.json'

def init_db():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    if not os.path.exists(BONUS_FILE):
        with open(BONUS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"balance": 0}, f, ensure_ascii=False, indent=4)

init_db()

# Начальное меню блюд (для демонстрации сценария)
MENU = [
    {"id": 1, "name": "Пицца Маргарита", "price": 450},
    {"id": 2, "name": "Пицца Пепперони", "price": 550},
    {"id": 3, "name": "Картофель фри", "price": 150},
    {"id": 4, "name": "Кока-кола", "price": 100}
]

# Простой HTML-интерфейс в виде строки для быстрой интеграции без создания папки templates
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>FoodDelivery v2.0</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f9f9f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .flex { display: flex; justify-content: space-between; align-items: center; }
        button { background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #218838; }
        .item-list { list-style: none; padding: 0; }
        .item-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .badge { background: #007bff; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>🍕 Панель FoodDelivery v2.0</h1>
    
    <div class="card">
        <h3>Ваш бонусный баланс: <span class="badge">{{ bonus_balance }} баллов</span></h3>
    </div>

    <div class="card">
        <h2>Меню блюд</h2>
        <ul class="item-list">
            {% for item in menu %}
            <li class="flex">
                <span><strong>{{ item.name }}</strong> — {{ item.price }} руб.</span>
                <form action="/add_to_order" method="POST" style="margin: 0;">
                    <input type="hidden" name="item_id" value="{{ item.id }}">
                    <button type="submit">Добавить в корзину</button>
                </form>
            </li>
            {% endfor %}
        </ul>
    </div>

    <div class="card">
        <h2>Оформление заказа</h2>
        <form action="/checkout" method="POST">
            <p>Промокод (введите SAVE10 для скидки 10%):</p>
            <input type="text" name="promocode" placeholder="Промокод">
            <br><br>
            <button type="submit" style="background: #ffc107; color: black;">Оформить заказ</button>
        </form>
    </div>

    <div class="card">
        <h2>📜 История заказов</h2>
        <ul class="item-list">
            {% for order in orders %}
            <li>
                <strong>Заказ №{{ loop.index }}</strong> | Сумма: {{ order.total }} руб. | Начислено бонусов: {{ order.bonuses_earned }}
            </li>
            {% else %}
            <p>История заказов пока пуста.</p>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
        orders = json.load(f)
    with open(BONUS_FILE, 'r', encoding='utf-8') as f:
        bonus = json.load(f)
    
    return render_template_string(HTML_TEMPLATE, menu=MENU, orders=orders, bonus_balance=bonus["balance"])

@app.route('/checkout', method=['POST'])
def checkout():
    # Симуляция заказа по умолчанию (две пиццы)
    total = 1000 
    promocode = request.form.get('promocode', '').strip()
    
    if promocode == "SAVE10":
        total = int(total * 0.9) # Применяем скидку 10%
        
    bonuses_earned = int(total * 0.1) # Кэшбэк 10%
    
    # Обновляем историю заказов
    with open(ORDERS_FILE, 'r+', encoding='utf-8') as f:
        orders = json.load(f)
        orders.append({"total": total, "bonuses_earned": bonuses_earned})
        f.seek(0)
        json.dump(orders, f, ensure_ascii=False, indent=4)
        
    # Обновляем бонусы
    with open(BONUS_FILE, 'r+', encoding='utf-8') as f:
        bonus = json.load(f)
        bonus["balance"] += bonuses_earned
        f.seek(0)
        json.dump(bonus, f, ensure_ascii=False, indent=4)
        
    return f"<h3>Заказ успешно оформлен! Сумма: {total} руб. Начислено бонусов: {bonuses_earned}.</h3><br><a href='/'>Назад на главную</a>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
