import json
import os

LEADERBOARD_FILE = 'leaderboard.json'

def load_leaderboard():
    """Загружает таблицу лидеров из файла."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Если файл пуст или поврежден, возвращаем пустой список
                return []
    else:
        # Если файла нет, возвращаем пустой список
        return []

def save_leaderboard(leaderboard_data):
    """Сохраняет таблицу лидеров в файл."""
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard_data, f, indent=4)

def add_score_to_leaderboard(time_taken, coins_collected, player_name="Player"):
    """Добавляет новый результат в таблицу лидеров."""
    leaderboard = load_leaderboard()
    leaderboard.append({'time': time_taken, 'coins': coins_collected, 'name': player_name})
    leaderboard.sort(key=lambda x: x['time']) # Сортировка по времени
    save_leaderboard(leaderboard)