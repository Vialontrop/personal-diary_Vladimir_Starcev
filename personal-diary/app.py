from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

FILE_NAME = 'entries.json'

# Задание 12.1. Функция загрузки записей из JSON
def load_entries():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Проверяем, что данные - список
                if isinstance(data, list):
                    return data
                else:
                    return []
        except (json.JSONDecodeError, IOError):
            return []
    return []

# Задание 12.2. Функция сохранения записей в JSON
def save_entries(entries):
    try:
        with open(FILE_NAME, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка при сохранении: {e}")

# Задание 12.3. Загрузка записей в переменную
entries = load_entries()

# Задание 13. Маршрут главной страницы
@app.route('/')
def index():
    return render_template('index.html', entries=entries)

# Задание 14. Маршрут просмотра записи
@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    entry = next((e for e in entries if e.get('id') == entry_id), None)
    if entry:
        return render_template('detail.html', entry=entry)
    return "Запись не найдена", 404

# Задание 15. Маршрут добавления записи
@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            return "Заголовок и текст не могут быть пустыми", 400
        
        # Генерация нового ID
        if entries:
            new_id = max(e.get('id', 0) for e in entries) + 1
        else:
            new_id = 1
        
        # Создание новой записи
        new_entry = {
            'id': new_id,
            'title': title,
            'content': content,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        
        entries.append(new_entry)
        save_entries(entries)
        return redirect('/')
    
    return render_template('add.html')

# Задание 16. Маршрут редактирования записи
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = next((e for e in entries if e.get('id') == entry_id), None)
    
    if not entry:
        return "Запись не найдена", 404
    
    if request.method == 'POST':
        entry['title'] = request.form.get('title', '').strip()
        entry['content'] = request.form.get('content', '').strip()
        save_entries(entries)
        return redirect('/')
    
    return render_template('edit.html', entry=entry)

# Задание 17. Маршрут удаления записи
@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    global entries
    entries = [e for e in entries if e.get('id') != entry_id]
    save_entries(entries)
    return redirect('/')

# Задание 18. Маршрут поиска
@app.route('/search')
def search_entries():
    query = request.args.get('q', '').strip()
    if query:
        filtered_entries = [e for e in entries if query.lower() in e.get('title', '').lower()]
    else:
        filtered_entries = entries
    return render_template('index.html', entries=filtered_entries)

# Задание 19. Маршрут фильтра по дате (последние 7 дней)
@app.route('/filter/week')
def filter_week():
    week_ago = datetime.now() - timedelta(days=7)
    filtered_entries = []
    
    for entry in entries:
        try:
            # Парсим дату из формата 'дд.мм.гггг ЧЧ:ММ'
            date_str = entry.get('date', '')
            if date_str and date_str != 'Дата неизвестна':
                entry_date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
                if entry_date >= week_ago:
                    filtered_entries.append(entry)
            else:
                # Если даты нет, пропускаем
                pass
        except (ValueError, KeyError):
            # Если дата не распарсилась, пропускаем запись
            pass
    
    # Добавляем информацию о фильтре в шаблон
    return render_template('index.html', entries=filtered_entries, filter_info="За последние 7 дней")