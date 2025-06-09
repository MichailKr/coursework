# leaderboard.py
import json
import os

LEADERBOARD_FILE = 'leaderboard.json'

def load_leaderboard():
    """Загружает таблицу лидеров из файла."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f: # Указываем кодировку
            try:
                # Загружаем данные, обрабатываем случай пустого файла
                data = json.load(f)
                if not isinstance(data, list): # Проверяем, что загружены данные в формате списка
                    return []
                return data
            except json.JSONDecodeError:
                # Если файл пуст или поврежден, возвращаем пустой список
                return []
    else:
        # Если файла нет, возвращаем пустой список
        return []

def save_leaderboard(leaderboard_data):
    """Сохраняет таблицу лидеров в файл."""
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f: # Указываем кодировку
        json.dump(leaderboard_data, f, indent=4, ensure_ascii=False) # ensure_ascii=False для сохранения кириллицы

def add_score_to_leaderboard(time_taken, coins_collected, player_name="Player"):
    """Добавляет новый результат в таблицу лидеров."""
    leaderboard = load_leaderboard()

    # Создаем новую запись
    new_entry = {'time': time_taken, 'coins': coins_collected, 'name': player_name}

    leaderboard.append(new_entry)

    # Сортировка по времени (по возрастанию)
    leaderboard.sort(key=lambda x: x.get('time', float('inf'))) # Используем .get() для безопасного доступа и float('inf') для отсутствующих значений

    # Опционально: ограничить количество записей в таблице лидеров
    # leaderboard = leaderboard[:15] # Например, хранить только топ-15

    save_leaderboard(leaderboard)