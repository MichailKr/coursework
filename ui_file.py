'''
User interface file
'''

import pygame
import time
import sys # Импортируем sys для использования sys.exit()

# Импорт функций для таблицы лидеров
from leaderboard import load_leaderboard, add_score_to_leaderboard # Убедимся, что add_score_to_leaderboard импортирована

# displays a horizontally-centred message to the screen
def displayMessage(text, colour, screen, size, screen_size, y_pos, screen_update=None):
    # set the font and size of the message
    # use print(pygame.font.get_fonts()) to see available fonts on system
    displayText = pygame.font.SysFont("ubuntu", size)
    # set the text surface
    textSurface = displayText.render(text, True, colour)
    # get the size of the rectangle surrounding the message
    textRect = textSurface.get_rect()
    # center the container
    textRect.center = ((screen_size[0]/2),y_pos)
    # print it to the screen
    screen.blit(textSurface,textRect)

    # if screen_update is not None and textRect.colliderect(screen_update):
    #    # update the screen with the message
    #    pygame.display.update(textRect.union(screen_update))
    # elif screen_update is not None:
    #      pygame.display.update(screen_update)
    # else:
    #    pygame.display.update(textRect)

    # Просто обновляем весь экран после отрисовки каждого сообщения для надежности в меню/экранах
    # В игровом цикле это делается в конце
    # pygame.display.flip() # Убрано, чтобы не обновлять каждый раз в цикле displayMenuSelection

    # return textRect

# displays the user selection of the Main Menu
# bg_colour: background colour, a_colout: active colour, na_colour: inactive colour
def displayMenuSelection(screen, screen_size, choice, bg_colour, a_colour, na_colour):
    background_image = pygame.image.load('fon.jpg').convert()
    background_image = pygame.transform.scale(background_image, screen.get_size())
    screen.blit(background_image, (0, 0))

    # Обновляем пункты меню, добавив "Таблица лидеров"
    menu_items = ["Dungeon of Kuksik", "Старт", "Настройки", "Таблица лидеров", "Выход"]

    # Рассчитываем вертикальный шаг между пунктами
    # Учитываем, что первый пункт - это заголовок и он не выбирается
    selectable_items_count = len(menu_items) - 1
    if selectable_items_count > 0:
       # Делим оставшееся пространство (высота экрана - отступ заголовка)
       # на количество выбираемых пунктов + 1 (для отступа после последнего пункта)
       item_spacing = (screen_size[1] - screen_size[1]//5) // (selectable_items_count + 1)
    else:
       item_spacing = 0 # Если нет выбираемых пунктов

    y_positions = []
    y_positions.append(screen_size[1]//5) # Позиция для заголовка
    for i in range(selectable_items_count):
       # Позиции выбираемых пунктов: отступ заголовка + (индекс пункта + 1) * шаг
       y_positions.append(screen_size[1]//5 + item_spacing * (i + 1))

    for i, item in enumerate(menu_items):
       if i == 0:  # Заголовок
          displayMessage(item, (249,166,2), screen, 50, screen_size, y_positions[i])  # Красный цвет
       else:  # Пункты меню
          # Индекс выбора для пунктов меню (0 для "Старт", 1 для "Настройки" и т.д.)
          selection_index_for_item = i - 1
          color = a_colour if selection_index_for_item == choice else na_colour
          displayMessage(item, color, screen, 30, screen_size, y_positions[i])
    pygame.display.flip()


# display settings options
# takes in additional grid size and side length parameters
def displaySettingsSeleciton(screen, screen_size, choice, bg_colour, a_colour, na_colour, grid_size, side_length,
							 mode_text):
	background_image = pygame.image.load('fon.jpg').convert()
	background_image = pygame.transform.scale(background_image, screen.get_size())
	screen.blit(background_image, (0, 0))

	# Формируем пункты меню
	items = [
		("Настройки", na_colour, 60, None), # Заголовок, используем na_colour для заголовка
		(f"Размер сетки: {grid_size}", a_colour if choice == 0 else na_colour, 30, None),
		(f"Длина клетки: {side_length}", a_colour if choice == 1 else na_colour, 30, None),
		(f"Режим: {mode_text}", a_colour if choice == 2 else na_colour, 30, None),
		("Вернуться", a_colour if choice == 3 else na_colour, 30, None)
	]

	# Увеличиваем расстояние между строками, например, до 70
	line_spacing = 60 # Уменьшил интервал для лучшего размещения на экране

	# Отрисовка пунктов меню с увеличенным интервалом
	start_y = screen_size[1] // 6 # Начальная позиция для заголовка
	for i, (text, color, size, _) in enumerate(items):
		y_position = start_y + i * line_spacing
		displayMessage(text, color, screen, size, screen_size, y_position)

	pygame.display.flip()


def settingsMenu(screen, screen_size, bg_colour, a_colour, na_colour, cooldown, start_timer, g_size, s_length): # Теперь принимаем screen и screen_size
    options = {0:"Размер сетки", 1:"Длина клетки", 2:"Режим", 3:"Назад"} # Обновили опции
    # Обновленный список режимов, чтобы соответствовать main.py
    modes = {0:"В одиночку", 1:"Вдвоем", 2:"Наперегонки", 3:"Преследование", 4:"Побег"}
    current_mode = 0 # Начинаем с режима "В одиночку" по умолчанию
    current_selection_index = 0 # Используем индекс для выбора

    grid_size = g_size
    side_length = s_length

    pygame.display.set_caption("Настройки")

    # Загружаем и отображаем фон один раз перед циклом
    background_image = pygame.image.load('fon.jpg').convert()
    background_image = pygame.transform.scale(background_image, screen.get_size())
    screen.blit(background_image, (0, 0))
    pygame.display.flip()

    # Отображаем начальное состояние меню настроек
    displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
                       grid_size, side_length, modes[current_mode])

    carryOn = True
    while carryOn:
       # action (close screen)
       for event in pygame.event.get():# user did something
          if event.type == pygame.QUIT:
             carryOn = False
             # Не закрываем pygame здесь, это делает main
             return g_size, s_length, current_mode # Возвращаем текущие настройки при выходе

       # get pressed keys
       keys = pygame.key.get_pressed()

       # if the cooldown timer is reached
       if (pygame.time.get_ticks() - start_timer > cooldown):
          if keys[pygame.K_DOWN]:
             current_selection_index = (current_selection_index + 1) % len(options)
             displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
                                grid_size, side_length, modes[current_mode])
             start_timer = pygame.time.get_ticks()
          elif keys[pygame.K_UP]:
             current_selection_index = (current_selection_index - 1) % len(options)
             displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
                                grid_size, side_length, modes[current_mode])
             start_timer = pygame.time.get_ticks()
          elif keys[pygame.K_LEFT] and current_selection_index in [0, 1, 2]: # Регулирование только для размера, длины и режима
             if current_selection_index == 0:
                grid_size = max(10, grid_size - 1)
             elif current_selection_index == 1:
                side_length = max(10, side_length - 1)
             elif current_selection_index == 2:
                current_mode = max(0, current_mode - 1)
             displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
                                grid_size, side_length, modes[current_mode])
             start_timer = pygame.time.get_ticks()
          elif keys[pygame.K_RIGHT] and current_selection_index in [0, 1, 2]:
             if current_selection_index == 0:
                grid_size = min(35, grid_size + 1)
             elif current_selection_index == 1:
                side_length = min(30, side_length + 1)
             elif current_selection_index == 2:
                 # Проверяем, чтобы не выйти за пределы существующих режимов (0 до 4)
                current_mode = min(len(modes) - 1, current_mode + 1)
             displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
                                grid_size, side_length, modes[current_mode])
             start_timer = pygame.time.get_ticks()
          elif keys[pygame.K_RETURN] and current_selection_index == 3: # Выход при выборе "Вернуться"
             carryOn = False

    # reset the caption
    pygame.display.set_caption("Главное меню")
    # return selected grid size, side length и mode
    return grid_size, side_length, current_mode

# start screen function
def startScreen(screen, screen_size): # Теперь принимаем screen и screen_size
    # Define colours
    BLACK = (0,0,0) # Добавляем локальный BLACK для фона
    WHITE = (255,255,255)
    GOLD = (249,166,2)

    pygame.display.set_caption("Главное меню")

    # Загружаем и отображаем фон один раз перед циклом
    background_image = pygame.image.load('fon.jpg').convert()
    background_image = pygame.transform.scale(background_image, screen.get_size())
    screen.blit(background_image, (0, 0))
    pygame.display.flip()

    options = {0:"Старт", 1:"Настройки", 2:"Таблица лидеров", 3:"Выход"} # Обновили опции меню
    current_selection_index = 0 # Используем индекс

    # Отображаем начальное состояние меню
    displayMenuSelection(screen, screen_size, current_selection_index, BLACK, GOLD, WHITE) # Используем BLACK как bg_colour

    clock = pygame.time.Clock()
    Run = True # Этот Run относится только к циклу этой функции
    carryOn = True # Флаг для цикла этой функции
    Settings = False
    next_state = 1 # Состояние для перехода после меню (по умолчанию игра)

    # Переменные для хранения выбора из настроек, инициализация перед циклом
    # Эти значения будут обновлены после выхода из settingsMenu
    selected_grid_size = 20 # Дефолтные значения, как в main
    selected_side_length = 22 # Дефолтные значения, как в main
    selected_mode = 0 # Дефолтный режим, как в main

    # set cooldown for key clicks
    cooldown = 150
    # initialize cooldown timer for key clicks
    start_timer = pygame.time.get_ticks()

    while carryOn:
       # action (close screen)
       for event in pygame.event.get():# user did something
          if event.type == pygame.QUIT:
             carryOn = False
             Run = False # Этот Run влияет на главный цикл в main
             next_state = -1 # Выход из игры

       # get pressed keys
       keys = pygame.key.get_pressed()

       # if the cooldown timer is reached
       if (pygame.time.get_ticks() - start_timer > cooldown):
          if keys[pygame.K_DOWN]:
             current_selection_index = (current_selection_index + 1) % len(options)
             displayMenuSelection(screen, screen_size, current_selection_index, BLACK, GOLD, WHITE) # Используем BLACK как bg_colour
             start_timer = pygame.time.get_ticks()
          elif keys[pygame.K_UP]:
             current_selection_index = (current_selection_index - 1) % len(options)
             displayMenuSelection(screen, screen_size, current_selection_index, BLACK, GOLD, WHITE) # Используем BLACK как bg_colour
             start_timer = pygame.time.get_ticks()
          elif keys[pygame.K_RETURN]:
             if current_selection_index == 0: # Start Game
                carryOn = False
                next_state = 1 # Переход к игре
             elif current_selection_index == 1: # Settings
                Settings = True
             elif current_selection_index == 2: # Таблица лидеров
                carryOn = False
                next_state = 2 # Переход к таблице лидеров
             elif current_selection_index == 3: # Exit
                carryOn = False
                Run = False
                next_state = -1 # Выход из игры

       # if the settings option was selected
       if Settings:
          # Передаем screen и screen_size в settingsMenu, а также текущие значения размеров и режима
          selected_grid_size, selected_side_length, selected_mode = settingsMenu(screen, screen_size, BLACK, GOLD, WHITE, cooldown,\
                                      start_timer, selected_grid_size, selected_side_length) # Используем BLACK как bg_colour
          # После выхода из настроек, возвращаемся в главное меню
          current_selection_index = 0
          displayMenuSelection(screen, screen_size, current_selection_index, BLACK, GOLD, WHITE) # Используем BLACK как bg_colour
          pygame.display.flip() # Обновляем экран
          time.sleep(0.25) # Небольшая задержка, чтобы избежать двойного нажатия
          start_timer = pygame.time.get_ticks() # Сбрасываем таймер после выхода из меню
          Settings = False # Сбрасываем флаг Settings

       clock.tick(60)

    # pygame.quit() # Не вызываем здесь, закрываем в main

    # Возвращаем флаг выполнения (для main), размеры, режим и следующее состояние
    return Run, selected_grid_size, selected_side_length, selected_mode, next_state


# Функция для отображения экрана ввода имени
def getInputNameScreen(screen, screen_size, time_taken, coins_collected):
	"""Отображает экран ввода имени игрока после соло игры."""
	pygame.display.set_caption("Введите имя")

	input_box = pygame.Rect(screen_size[0] // 4, screen_size[1] // 2 - 20, screen_size[0] // 2, 40)
	color_inactive = pygame.Color('lightskyblue3')
	color_active = pygame.Color('dodgerblue2')
	color = color_inactive
	active = False
	text = ''
	font = pygame.font.SysFont("ubuntu", 32)
	done = False

	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
				text = "" # Возвращаем пустую строку при закрытии окна или sys.exit()
				# sys.exit() # Можно использовать sys.exit() для полного выхода из приложения
			if event.type == pygame.MOUSEBUTTONDOWN:
				# If the user clicked on the input_box rect.
				if input_box.collidepoint(event.pos):
					# Toggle the active flag.
					active = not active
				else:
					active = False
				# Change the current color of the input box.
				color = color_active if active else color_inactive
			if event.type == pygame.KEYDOWN:
				if active:
					if event.key == pygame.K_RETURN:
						done = True
					elif event.key == pygame.K_BACKSPACE:
						text = text[:-1]
					else:
						text += event.unicode
				elif event.key == pygame.K_ESCAPE: # Добавляем возможность выйти из ввода имени по Esc
					done = True
					text = "" # Возвращаем пустую строку при отмене

		# Загружаем и отображаем фоновое изображение
		bg_image = pygame.image.load('fon.jpg')
		bg_image = pygame.transform.scale(bg_image, screen_size)
		screen.blit(bg_image, (0, 0))

		# Заголовок
		title_font = pygame.font.SysFont("ubuntu", 50)
		title_text_surface = title_font.render("Игра окончена!", True, (255, 255, 255))
		title_text_rect = title_text_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 4))
		screen.blit(title_text_surface, title_text_rect)

		# Информация о результате
		result_font = pygame.font.SysFont("ubuntu", 30)
		result_text_surface = result_font.render(f"Время: {time_taken:.2f} сек, Монеты: {coins_collected}", True, (255, 255, 255))
		result_text_rect = result_text_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 3))
		screen.blit(result_text_surface, result_text_rect)

		# Подсказка для ввода имени
		prompt_font = pygame.font.SysFont("ubuntu", 25)
		prompt_text_surface = prompt_font.render("Введите ваше имя:", True, (255, 255, 255))
		prompt_text_rect = prompt_text_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 - 40))
		screen.blit(prompt_text_surface, prompt_text_rect)


		# Render the current text.
		txt_surface = font.render(text, True, color)
		# Resize the box if the text is too long.
		width = max(screen_size[0] // 4, txt_surface.get_width()+10) # Уменьшил минимальную ширину поля ввода
		input_box.w = width
		# Center the input box
		input_box.x = screen_size[0] // 2 - input_box.w // 2
		# Draw the input box.
		pygame.draw.rect(screen, color, input_box, 2)
		# Blit the text.
		screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

		# Инструкция для сохранения/отмены
		instruction_font = pygame.font.SysFont("ubuntu", 20)
		instruction_text_surface = instruction_font.render("Нажмите Enter для сохранения, Esc для отмены", True, (255, 255, 255))
		instruction_text_rect = instruction_text_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 + 40))
		screen.blit(instruction_text_surface, instruction_text_rect)


		pygame.display.flip()

	pygame.display.set_caption("Главное меню")
	return text.strip() # Возвращаем введенное имя, удаляя пробелы по краям


# Функция для отображения таблицы лидеров
# import pygame # Уже импортирован в начале файла

def display_leaderboard_screen(screen, font, leaderboard_data, sort_by='time', screen_size=(800, 600)):
    """Отображает экран таблицы лидеров с фоном fon.jpg и сортировкой."""

    # Загружаем и отображаем фоновое изображение
    bg_image = pygame.image.load('fon.jpg')
    bg_image = pygame.transform.scale(bg_image, screen_size)
    screen.blit(bg_image, (0, 0))

    # Заголовок
    title_font_large = pygame.font.SysFont("ubuntu", 50) # Увеличил размер шрифта заголовка
    title_text = title_font_large.render("Таблица лидеров", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(screen_size[0] // 2, 50))
    screen.blit(title_text, title_rect)

    # Сортировка данных
    if sort_by == 'time':
        # Сортируем по времени (по возрастанию), обрабатываем случаи отсутствия ключа
        sorted_data = sorted(leaderboard_data, key=lambda x: x.get('time', float('inf')))
        sort_title = "по времени (сек)"
    elif sort_by == 'coins':
        # Сортируем по монетам (по убыванию), обрабатываем случаи отсутствия ключа
        sorted_data = sorted(leaderboard_data, key=lambda x: x.get('coins', 0), reverse=True)
        sort_title = "по монетам"
    else:
        sorted_data = leaderboard_data
        sort_title = ""

    # Отображение типа сортировки
    sort_type_font = pygame.font.SysFont("ubuntu", 25) # Уменьшил размер шрифта для типа сортировки
    sort_type_text = sort_type_font.render(f"Сортировка: {sort_title}", True, (255, 255, 255))
    screen.blit(sort_type_text, (50, 110)) # Скорректировал вертикальную позицию

    # Отображение топ-15
    y_offset = 150
    x_pos = 50 # Начальная позиция по X
    # Увеличиваем доступную ширину, чтобы текст лучше помещался
    max_line_width = screen_size[0] - x_pos * 2
    line_height = 25 # Уменьшил расстояние между строками для плотной таблицы

    score_font = pygame.font.SysFont("ubuntu", 22) # Уменьшил размер шрифта для элементов списка

    for i, entry in enumerate(sorted_data[:15]):
        # Форматируем строку с учетом возможного отсутствия ключей и ограничивая длину имени
        player_name = entry.get('name', 'Игрок') # Не будем жестко ограничивать имя здесь
        time_str = f"{entry.get('time', 0):.2f}" if 'time' in entry else "N/A"
        coins_str = f"{entry.get('coins', 0)}" if 'coins' in entry else "N/A"
        # Рассчитываем "Счет" только если есть время и монеты, избегая деления на ноль
        score_value = 0
        if 'time' in entry and entry['time'] > 0:
             score_value = (entry.get('coins', 0) * 10000 + 10000) / entry['time']

        score_str = f"{score_value:.2f}"

        # Собираем строку для отображения
        score_line = f"{i + 1}. {player_name} - Время: {time_str}, Монеты: {coins_str}, Счет: {score_str}"

        # Отрисовываем текст
        score_text_surface = score_font.render(score_line, True, (255, 255, 255))

        # Проверяем, не выходит ли текст за границы, и если да, усекаем его
        if score_text_surface.get_width() > max_line_width:
            # Простой способ усечения: находим, сколько символов помещается
            # Это не идеальное решение для русского языка из-за разной ширины символов
            # Для более точного усечения нужна посимвольная проверка
            available_chars = int(max_line_width / score_font.size(' ')[0] * 0.8) # Примерная оценка
            truncated_line = score_line[:available_chars] + "..." if len(score_line) > available_chars else score_line
            score_text_surface = score_font.render(truncated_line, True, (255, 255, 255))


        screen.blit(score_text_surface, (x_pos, y_offset + i * line_height))

    # Инструкции по сортировке и выходу
    instructions_font = pygame.font.SysFont("ubuntu", 20)
    instructions_text = instructions_font.render(
        "Нажмите T для сортировки по времени, C для сортировки по монетам, Esc для выхода", True, (255, 255, 255)
    )
    instructions_rect = instructions_text.get_rect(center=(screen_size[0] // 2, screen_size[1] - 30))
    screen.blit(instructions_text, instructions_rect)

    pygame.display.flip()

    return True

def leaderboardScreen(screen, screen_size):
    """Экран таблицы лидеров с фоном fon.jpg и сортировкой."""
    pygame.display.set_caption("Таблица лидеров")
    # Фонт для отображения элементов списка
    font = pygame.font.SysFont("ubuntu", 30) # Изначальный размер шрифта, может быть скорректирован в display_leaderboard_screen

    current_sort = 'time'  # По умолчанию сортировка по времени
    leaderboard_data = load_leaderboard() # Загружаем данные

    carryOn = True
    while carryOn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False
                # Не закрываем pygame здесь, это делает main
                return -1 # Сигнал для выхода из главного цикла
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    carryOn = False
                elif event.key == pygame.K_t:
                    current_sort = 'time'
                    leaderboard_data = load_leaderboard() # Перезагружаем данные при смене сортировки
                elif event.key == pygame.K_c:
                    current_sort = 'coins'
                    leaderboard_data = load_leaderboard() # Перезагружаем данные при смене сортировки

        # Отображаем экран таблицы лидеров
        display_leaderboard_screen(screen, font, leaderboard_data, sort_by=current_sort, screen_size=screen_size)

        # Небольшая задержка для снижения нагрузки на ЦП
        pygame.time.Clock().tick(60)


    pygame.display.set_caption("Главное меню")
    return 0 # Возвращаемся в главное меню


def endGame(mode, value):
    screen = pygame.display.get_surface()
    screen_size = screen.get_size()

    # Define colours
    WHITE = (255,255,255)
    GOLD = (249,166,2)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    RED = (255,0,0)

    pygame.display.set_caption("Игра окончена")

    background_image = pygame.image.load('fon.jpg').convert()
    background_image = pygame.transform.scale(background_image, screen.get_size())
    screen.blit(background_image, (0, 0))
    pygame.display.flip()

    # Общий заголовок "Игра окончена"
    displayMessage("Игра окончена", WHITE, screen, 50, screen_size, screen_size[1]//4)

    # Текст результата в зависимости от режима
    if mode == 0:
       text = "Вы проиграли!"
       displayMessage(text, RED, screen, 30, screen_size, screen_size[1]*2//4)
    elif mode == 1:
       text = "Игрок " + str(value) + " победил!"
       color = GREEN if value == 1 else BLUE
       displayMessage(text, color, screen, 30, screen_size, screen_size[1]*2//4)
    elif mode in [2, 3]:
       if value == 1:
          text = "Вы победили!"
          displayMessage(text, GOLD, screen, 30, screen_size, screen_size[1]*2//4)
       else:
          text = "Куксик победил!"
          displayMessage(text, RED, screen, 30, screen_size, screen_size[1]*2//4)
    elif mode == 4:
       if value == 1:
          text = "Вы победили!!"
          displayMessage(text, GOLD, screen, 30, screen_size, screen_size[1]*2//4)
       else:
          text = "Вы проиграли!!"
          displayMessage(text, RED, screen, 30, screen_size, screen_size[1]*2//4)
    pygame.display.flip()


    # Инструкция по выходу
    displayMessage("Нажмите Enter чтобы выйти в меню.", WHITE, screen, 20, screen_size, screen_size[1] * 3 // 4)


    carryOn = True
    clock = pygame.time.Clock()
    while carryOn:
       # action (close screen)
       for event in pygame.event.get():# user did something
          if event.type == pygame.QUIT:
             carryOn = False
             # sys.exit() # Можно использовать sys.exit() для полного выхода

       # get keys pressed
       keys = pygame.key.get_pressed()
       if keys[pygame.K_RETURN]:
          carryOn = False

       clock.tick(60)

    # pygame.quit() # Не вызываем здесь