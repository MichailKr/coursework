'''
User interface file
'''

import pygame
import time
# Импорт функций для таблицы лидеров
from leaderboard import load_leaderboard

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
	# if no secified update screen size
	if screen_update is None:
		screen_update = textRect
	# update the screen with the message
	pygame.display.update(screen_update)
	# print(textRect)
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
			color = (255, 0,
					 0) if i - 1 == choice else na_colour  # Все пункты красные, активный - красный, остальные - na_colour
			displayMessage(item, color, screen, 30, screen_size, y_positions[i])


# display settings options
# takes in additional grid size and side length parameters
def displaySettingsSeleciton(screen, screen_size, choice, bg_colour, a_colour, na_colour, grid_size, side_length, mode_text):
	background_image = pygame.image.load('fon.jpg').convert()
	background_image = pygame.transform.scale(background_image, screen.get_size())
	screen.blit(background_image, (0, 0))
	grid_text = "Размер сетки: " + str(grid_size)
	side_text = "Длина клетки: " + str(side_length)
	# this is the position of the largest rectangle for mode text to update
	mode_text_rect = (176,316,149,34) # Возможно, эту координату тоже нужно пересчитать для нового размера экрана

	# Обновляем индексы выбора
	items = [
		("Settings", na_colour, 60, screen_size[1]//6),
		# Используем BLACK для невыбранных пунктов в меню настроек
		(grid_text, a_colour if choice == 0 else (255, 255, 255), 30, screen_size[1]*2//6), # BLACK = (0, 0, 0)
		(side_text, a_colour if choice == 1 else (255, 255, 255), 30, screen_size[1]*3//6), # BLACK = (0, 0, 0)
		(mode_text, a_colour if choice == 2 else (255, 255, 255), 30, screen_size[1]*4//6), # BLACK = (0, 0, 0)
		("Return", a_colour if choice == 3 else (255, 255, 255), 30, screen_size[1]*5//6) # BLACK = (0, 0, 0)
	]

	for i, (text, color, size, y_pos) in enumerate(items):
		# Передаем screen_size в displayMessage
		displayMessage(text, color, screen, size, screen_size, y_pos, mode_text_rect if i == 3 else None) # Передаем обновленный цвет


# settings function - enables user to choose size of the map
def settingsMenu(screen, screen_size, bg_colour, a_colour, na_colour, cooldown, start_timer, g_size, s_length): # Теперь принимаем screen и screen_size
	options = {0:"Размер сетки", 1:"Длина клетки", 2:"Режим", 3:"Назад"} # Обновили опции
	modes = {0:"В одиночку", 1:"Вдвоем", 2:"Race", 3:"Chase", 4:"Escape"}
	current_mode = 0
	current_selection_index = 0 # Используем индекс для выбора
	grid_size = g_size
	side_length = s_length

	pygame.display.set_caption("Настройки")
	background_image = pygame.image.load('fon.jpg').convert()
	background_image = pygame.transform.scale(background_image, screen.get_size())
	screen.blit(background_image, (0, 0))
	pygame.display.flip()

	displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
							 grid_size, side_length, modes[current_mode])

	carryOn = True
	while carryOn:
		# action (close screen)
		for event in pygame.event.get():# user did something
			if event.type == pygame.QUIT:
				carryOn = False
				# Здесь нет Run = False, так как эта функция вызывается из startScreen


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
					current_mode = min(4, current_mode + 1)
				displaySettingsSeleciton(screen, screen_size, current_selection_index, bg_colour, a_colour, na_colour,\
										 grid_size, side_length, modes[current_mode])
				start_timer = pygame.time.get_ticks()
			elif keys[pygame.K_RETURN] and current_selection_index == 3: # Выход при выборе "Return"1510
				carryOn = False


	# reset the caption
	pygame.display.set_caption("Главное меню")
	# return selected grid size, side length и mode
	return grid_size, side_length, current_mode

# start screen function
def startScreen(screen, screen_size): # Теперь принимаем screen и screen_size
	# pygame.init() # Не вызываем здесь, инициализация в main
	# default maze settings - эти значения теперь задаются в main
	# grid_size = 20 # Удаляем инициализацию
	# side_length = 10 # Удаляем инициализацию15
	# mode = 0 # Удаляем инициализацию

	# Define colours
	BLACK = (0,0,0)
	WHITE = (255,255,255)
	GOLD = (249,166,2)
	# screen_size = (800,600) # Размер окна задается в main и передается сюда
	# screen = pygame.display.set_mode(screen_size) # Не создаем новое окно, используем переданное
	pygame.display.set_caption("Главное меню")
	screen.fill(WHITE)
	pygame.display.flip()

	options = {0:"Старт", 1:"Настройки", 2:"Таблица лидеров", 3:"Выход"} # Обновили опции меню
	current_selection_index = 0 # Используем индекс
	displayMenuSelection(screen, screen_size, current_selection_index, WHITE, GOLD, BLACK)

	clock = pygame.time.Clock()


	Run = True # Этот Run относится только к циклу этой функции
	carryOn = True # Флаг для цикла этой функции
	Settings = False
	next_state = 1 # Состояние для перехода после меню (по умолчанию игра)

    # Переменные для хранения выбора из настроек, инициализация перед циклом
	# Эти значения будут обновлены после выхода из settingsMenu
	selected_grid_size = 20 # Дефолтные значения, как в main
	selected_side_length = 22
	selected_mode = 0


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
				displayMenuSelection(screen, screen_size, current_selection_index, WHITE, GOLD, BLACK)
				start_timer = pygame.time.get_ticks()
			elif keys[pygame.K_UP]:
				current_selection_index = (current_selection_index - 1) % len(options)
				displayMenuSelection(screen, screen_size, current_selection_index, WHITE, GOLD, BLACK)
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
			selected_grid_size, selected_side_length, selected_mode = settingsMenu(screen, screen_size, WHITE, GOLD, BLACK, cooldown,\
											 	 start_timer, selected_grid_size, selected_side_length)
			# После выхода из настроек, возвращаемся в главное меню
			current_selection_index = 0
			displayMenuSelection(screen, screen_size, current_selection_index, WHITE, GOLD, BLACK)
			pygame.display.flip() # Обновляем экран
			time.sleep(0.25)
			start_timer = pygame.time.get_ticks()
			Settings = False


		clock.tick(60)

	# pygame.quit() # Не вызываем здесь, закрываем в main

	# Возвращаем флаг выполнения (для main), размеры, режим и следующее состояние
	return Run, selected_grid_size, selected_side_length, selected_mode, next_state

# Функция для отображения таблицы лидеров
def display_leaderboard_screen(screen, font, leaderboard_data, sort_by='time', screen_size=(800, 600)): # Установили дефолтный размер побольше
	"""Отображает экран таблицы лидеров."""
	screen.fill((0, 0, 0)) # Черный фон
	title_text = font.render("Таблица лидеров", True, (255, 255, 255))
	# Центрируем заголовок по новому размеру
	title_rect = title_text.get_rect(center=(screen_size[0] // 2, 50))
	screen.blit(title_text, title_rect)

	# Сортируем данные
	if sort_by == 'time':
		sorted_data = sorted(leaderboard_data, key=lambda x: x.get('time', 0)) # Добавил .get с дефолтным значением на случай отсутствия ключа
		sort_title = "по времени (сек)"
	elif sort_by == 'coins':
		sorted_data = sorted(leaderboard_data, key=lambda x: x.get('coins', 0), reverse=True)
		sort_title = "по монетам"
	else:
		sorted_data = leaderboard_data
		sort_title = ""

	sort_type_text = font.render(f"Сортировка: {sort_title}", True, (255, 255, 255))
	screen.blit(sort_type_text, (50, 100))


	y_offset = 150
	for i, entry in enumerate(sorted_data[:15]): # Отображаем топ-15
		# Отображаем время с двумя знаками после запятой
		score_text = font.render(
			f"{i+1}. {entry.get('name', 'Player')} - Время: {entry.get('time', 0):.2f} сек, Монеты: {entry.get('coins', 0)}",
			True, (255, 255, 255)
		)
		screen.blit(score_text, (50, y_offset + i * 30))

	# Добавляем инструкции по сортировке и выходу, центрируя по новой высоте
	instructions_font = pygame.font.SysFont("ubuntu", 20)
	instructions_text = instructions_font.render("Нажмите T для сортировки по времени, C для сортировки по монетам, Esc для выхода", True, (255, 255, 255))
	instructions_rect = instructions_text.get_rect(center=(screen_size[0] // 2, screen_size[1] - 30)) # Центрируем по горизонтали, немного выше нижнего края
	screen.blit(instructions_text, instructions_rect)


	pygame.display.flip()

	# Возвращаем признак того, нужно ли продолжать отображение таблицы
	return True

# Функция для экрана таблицы лидеров
def leaderboardScreen(screen, screen_size): # screen_size теперь передается
	pygame.display.set_caption("Таблица лидеров")
	font = pygame.font.SysFont("ubuntu", 30)
	current_sort = 'time' # Сортировка по умолчанию
	leaderboard_data = load_leaderboard() # Загружаем данные

	carryOn = True
	while carryOn:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				carryOn = False
				return -1 # Сигнал выхода из игры
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					carryOn = False
				elif event.key == pygame.K_t:
					current_sort = 'time'
				elif event.key == pygame.K_c:
					current_sort = 'coins'

		# Передаем screen_size в display_leaderboard_screen
		display_leaderboard_screen(screen, font, leaderboard_data, sort_by=current_sort, screen_size=screen_size)

	pygame.display.set_caption("Main Menu")
	return 0 # Возвращаемся в главное меню

# end game screen
def endGame(mode, value): # Не принимаем screen и screen_size, так как они будут доступны через pygame.display.get_surface()
	# pygame.init() # Не вызываем здесь
	screen = pygame.display.get_surface() # Получаем текущую поверхность
	screen_size = screen.get_size() # Получаем текущий размер

	# Define colours
	BLACK = (0,0,0)
	GRAY = (100,100,100)
	WHITE = (255,255,255)
	GOLD = (249,166,2)
	GREEN = (0,255,0)
	BLUE = (0,0,255)

	pygame.display.set_caption("Game Over")
	screen.fill(WHITE)
	pygame.display.flip() # Добавляем явное обновление экрана после заливки

	if mode == 0:
		# Для режима Solo, value - это время
		text = f"Время: {value:.2f} сек" # Отображаем время с двумя знаками после запятой
		displayMessage("Game Over", BLACK, screen, 50, screen_size, screen_size[1]//4)
		displayMessage(text, BLACK, screen, 30, screen_size, screen_size[1]*2//4)
		displayMessage("Press enter to exit to menu.", BLACK, screen, 20, screen_size,screen_size[1]*3//4)
	elif mode == 1:
		text = "Player " + str(value) + " wins!"
		displayMessage("Game Over", BLACK, screen, 50, screen_size, screen_size[1]//4)
		if value == 1:
			displayMessage(text, GREEN, screen, 30, screen_size, screen_size[1]*2//4)
		else:
			displayMessage(text, BLUE, screen, 30, screen_size, screen_size[1]*2//4)
		displayMessage("Press enter to exit to menu.", BLACK, screen, 20, screen_size,screen_size[1]*3//4)
	elif mode == 2 or mode == 3:
		displayMessage("Game Over", BLACK, screen, 50, screen_size, screen_size[1]//4)
		if value == 1:
			text = "You win!"
			displayMessage(text, GOLD, screen, 30, screen_size, screen_size[1]*2//4)
		else:
			text = "The computer wins!"
			displayMessage(text, GRAY, screen, 30, screen_size, screen_size[1]*2//4)
		displayMessage("Press enter to exit to menu.", BLACK, screen, 20, screen_size,screen_size[1]*3//4)
	elif mode == 4:
		displayMessage("Game Over", BLACK, screen, 50, screen_size, screen_size[1]//4)
		if value == 1:
			text = "You escaped!"
			displayMessage(text, GOLD, screen, 30, screen_size, screen_size[1]*2//4)
		else:
			text = "You were caught!"
			displayMessage(text, GRAY, screen, 30, screen_size, screen_size[1]*2//4)
		displayMessage("Press enter to exit to menu.", BLACK, screen, 20, screen_size,screen_size[1]*3//4)

	carryOn = True
	clock = pygame.time.Clock()
	while carryOn:
		# action (close screen)
		for event in pygame.event.get():# user did something
			if event.type == pygame.QUIT:
				carryOn = False
		# get keys pressed
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RETURN]:
			carryOn = False
		clock.tick(60)

	# pygame.quit() # Не вызываем здесь