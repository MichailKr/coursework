from graph import Graph
from character import Character
import ui_file
import astar
import random
import pygame
import time
import queue
from collections import deque
import os
# Импорт функций для таблицы лидеров
from leaderboard import load_leaderboard, add_score_to_leaderboard

# function to set the position of the display window
def set_window_position(x, y):
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

def load_background(screen):
    fon = pygame.image.load('fon.jpg').convert()
    fon = pygame.transform.scale(fon, screen.get_size())
    return fon

# creates a grid of size (size)*(size)
def create_grid(size):
	# create a graph for the grid
	grid = Graph()
	# add the vertices of the grid
	for i in range(size):
		for j in range(size):
			grid.add_vertex((i,j))
	# return the constructed grid
	return grid

# creates a maze when a grid ad its vertices are passed in
def create_maze(grid, vertex, completed=None, vertices=None):
	if vertices is None:
		vertices = grid.get_vertices()
	if completed is None:
		completed = [vertex]
	# select a random direction
	paths = list(int(i) for i in range(4))
	random.shuffle(paths)
	# vertices in the direction from current vertex
	up = (vertex[0],vertex[1]-1)
	down = (vertex[0],vertex[1]+1)
	left = (vertex[0]-1,vertex[1])
	right = (vertex[0]+1,vertex[1])
	for direction in paths:
		if direction == 0:
			if up in vertices and up not in completed:
				# add the edges
				grid.add_edge((vertex,up))
				grid.add_edge((up,vertex))
				completed.append(up)
				create_maze(grid, up, completed, vertices)
		elif direction == 1:
			if down in vertices and down not in completed:
				grid.add_edge((vertex,down))
				grid.add_edge((down,vertex))
				completed.append(down)
				create_maze(grid, down, completed, vertices)
		elif direction == 2:
			if left in vertices and left not in completed:
				grid.add_edge((vertex,left))
				grid.add_edge((left,vertex))
				completed.append(left)
				create_maze(grid, left, completed, vertices)
		elif direction == 3:
			if right in vertices and right not in completed:
				grid.add_edge((vertex,right))
				grid.add_edge((right,vertex))
				completed.append(right)
				create_maze(grid, right, completed, vertices)
	return grid

# draw maze function
# takes in a (size)x(size) maze and prints a "colour" path
# side_length is the length of the grid unit and border_width is its border thickness
# offset_x: смещение по X для отрисовки лабиринта (для размещения HUD справа)
def draw_maze(screen, maze, size, colour, side_length, border_width, offset_x):
	# for every vertex in the maze:
	for i in range(size):
		for j in range(size):
			# if the vertex is not at the left-most side of the map
			if (i != 0):
				# check if the grid unit to the current unit's left is connected by an edge
				if maze.is_edge(((i,j),(i-1,j))):
					# if connected, draw the grid unit without the left wall
					pygame.draw.rect(screen,colour,[offset_x + (side_length+border_width)*i, border_width+(side_length+border_width)*j,\
									 side_length+border_width, side_length])
			# if the vertex is not at the right-most side of the map
			if (i != size-1):
				if maze.is_edge(((i,j),(i+1,j))):
					# draw the grid unit without the right wall (extend by border_width)
					pygame.draw.rect(screen,colour,[offset_x + border_width+(side_length+border_width)*i,\
									 border_width+(side_length+border_width)*j, side_length+border_width, side_length])
			# if the vertex is not at the top-most side of the map
			if (j != 0):
				if maze.is_edge(((i,j),(i,j-1))):
					pygame.draw.rect(screen,colour,[offset_x + border_width+(side_length+border_width)*i,\
									 (side_length+border_width)*j, side_length, side_length+border_width])
			# if the vertex is not at the bottom-most side of the map
			if (j != size-1):
				if maze.is_edge(((i,j),(i,j+1))):
					pygame.draw.rect(screen,colour,[offset_x + border_width+(side_length+border_width)*i,\
									 border_width+(side_length+border_width)*j, side_length, side_length+border_width])

# draw position of grid unit
# offset_x: смещение по X для отрисовки (для размещения HUD справа)
def draw_position(screen, side_length, border_width, current_point, colour, offset_x):
	pygame.draw.rect(screen, colour, [offset_x + border_width+(side_length+border_width)*current_point[0],\
					 border_width+(side_length+border_width)*current_point[1], side_length, side_length])


def draw_coin(screen, coin_image, current_point, side_length, border_width, offset_x, scale_factor=1):
	# Масштабируем изображение
	new_width = int(coin_image.get_width() * scale_factor)
	new_height = int(coin_image.get_height() * scale_factor)
	scaled_image = pygame.transform.scale(coin_image, (new_width, new_height))

	x = offset_x + border_width + (side_length + border_width) * current_point[0]
	y = border_width + (side_length + border_width) * current_point[1]
	# Центрируем изображение в клетке
	image_rect = scaled_image.get_rect()
	image_rect.center = (x + side_length // 2, y + side_length // 2)
	screen.blit(scaled_image, image_rect)

# takes in a player2 character, maze, vertices, cooldown, and timer
def playerTwo(player2, maze, vertices, cooldown, timer):
	# get the pressed keys
	keys = pygame.key.get_pressed()
	if (pygame.time.get_ticks() - timer > cooldown):
		current_point = player2.get_current_position()
		# move character right
		if keys[pygame.K_d]:
			# check if the next point is in the maze
			if (current_point[0]+1, current_point[1]) in vertices:
				next_point = (current_point[0]+1, current_point[1])
				# check if the next point is connected by an edge
				if (maze.is_edge((current_point,next_point))):
					player2.move_character_smooth(next_point,5)
			# restart cooldown timer
			timer = pygame.time.get_ticks()
		# move character left
		if keys[pygame.K_a]:
			if (current_point[0]-1,current_point[1]) in vertices:
				next_point = (current_point[0]-1, current_point[1])
				if (maze.is_edge((current_point,next_point))):
					player2.move_character_smooth(next_point,5)
			# restart cooldown timer
			timer = pygame.time.get_ticks()
		# move character up
		if keys[pygame.K_w]:
			if (current_point[0],current_point[1]-1) in vertices:
				next_point = (current_point[0], current_point[1]-1)
				if (maze.is_edge((current_point,next_point))):
					player2.move_character_smooth(next_point,5)
			# restart cooldown timer
			timer = pygame.time.get_ticks()
		# move character down
		if keys[pygame.K_s]:
			if (current_point[0],current_point[1]+1) in vertices:
				next_point = (current_point[0], current_point[1]+1)
				if (maze.is_edge((current_point,next_point))):
					player2.move_character_smooth(next_point,5)
			# restart cooldown timer
			timer = pygame.time.get_ticks()
	return timer

# update path function for chase mode
def update_path(next_point, deque):
	if len(deque) >= 2:
		# get the current point before the move
		first_pop = deque.pop()
		# get the previous point
		second_pop = deque.pop()
		# if the player backtracks (previous point == next point)
		if second_pop == next_point:
			# only append the previous point
			deque.append(second_pop)
		else:
			# add all the points back to the deque including the next point
			deque.append(second_pop)
			deque.append(first_pop)
			deque.append(next_point)
		# return the deque
		return deque
	else:
		# if the deque only has its initial point
		deque.append(next_point)
		# return the deque
		return deque

# astar update path function
def update_path_a(start_point, end_point, maze, deque):
	# get the shortest path using astar
	closest_path = astar.astar(start_point, end_point, maze)
	# starting point is not needed
	closest_path.remove(start_point)
	# if the current path has more points than the closest path by astar,
	# load the deque with the new set of points from a_star
	if len(deque)+1 > len(closest_path):
		# clear the existing deque
		deque.clear()
		# append the new edges
		for edge in closest_path:
			deque.append(edge)
		# return the new deque
		return deque
	# if not, update the path as usual
	else:
		# return the deque with the appended path, end_point acts as the next point
		return update_path(end_point, deque)

# break wall function just for escape mode
def break_wall(maze, current_point, next_point):
	# if there is no path from the current point to the next point, make one
	if not maze.is_edge((current_point,next_point)):
		maze.add_edge((current_point,next_point))
		maze.add_edge((next_point,current_point))
	# return the new maze
	return maze

# update console function for escape mode
# offset_x: смещение по X для консоли (для размещения HUD справа)
def update_console(screen, screen_size, side_length, text_size, a_colour, na_colour, keys_left, wallBreaks, offset_x):
	if keys_left == 0:
		text = "Escape! " + " WB: " + str(wallBreaks)
	else:
		text = "K: " + str(keys_left) + " WB: " + str(wallBreaks)
	# console rect
	# Ширина консоли теперь ограничена областью лабиринта
	console_rect = (offset_x, screen_size[1]-side_length*3, screen_size[0] - offset_x, side_length*3) # Скорректирована ширина и позиция
	# clear console
	pygame.draw.rect(screen, na_colour,console_rect)
	# display the text
	displayText = pygame.font.SysFont("ubuntu", text_size)
	textSurface = displayText.render(text, True, a_colour)
	textRect = textSurface.get_rect()
	# center text - центрируем относительно области лабиринта
	textRect.center = (offset_x + (screen_size[0] - offset_x) / 2, screen_size[1]-text_size*2) # Скорректировано центрирование
	# display text on screen ("blit")
	screen.blit(textSurface,textRect)
	# update the screen
	pygame.display.update(console_rect)

# run the maze game
# takes in a game mode parameter along with grid size and side length for the maze
def runGame(screen, screen_size, grid_size, side_length, mode): # Теперь принимаем screen и screen_size
	# initialize the game engine
	# pygame.init() # Не вызываем здесь, инициализация в main
	coin_image = pygame.image.load('coin.png').convert_alpha()
	acc_image = pygame.image.load('acc.png').convert_alpha()
	slow_image = pygame.image.load('slow.png').convert_alpha()
	# Defining colours (RGB) ...
	BLACK = (0,0,0)
	GRAY = (100,100,100)
	WHITE = (111,22,125)
	GOLD = (249,166,2)
	GREEN = (0,255,0)
	RED = (255,0,0)
	BLUE = (0,0,255)
	COIN_COLOR = GOLD # Цвет монет
	ACCELERATOR_COLOR = (0, 255, 255) # Цвет ускорителя (Cyan)
	SLOWDOWN_COLOR = (255, 0, 255) # Цвет замедлителя (Magenta)Таблица
	HUD_BG_COLOR = (30, 30, 30) # Цвет фона HUD панели

	# set the grid size and side length of each grid
	# grid_size = 20 # this is the maximum size before reaching recursion limit on maze buidling function
	# side_length = 10

	# scale the border width with respect to the given side length
	border_width = side_length//5

	# --- Расчет размеров окна с HUD ---
	maze_width = grid_size * (side_length + border_width) + border_width
	maze_height = grid_size * (side_length + border_width) + border_width
	hud_width = 200 # Фиксированная ширина HUD панели справа
	game_screen_width = maze_width + hud_width # Общая ширина окна
	game_screen_height = maze_height
	offset_x = hud_width # Смещение по X для отрисовки лабиринта и персонажей

	if mode == 4: # Если режим Escape, добавляем место для консоли снизу
		game_screen_height += side_length * 3

	# Проверяем, если текущий размер окна отличается, меняем его
	current_window_size = pygame.display.get_surface().get_size()
	if current_window_size != (game_screen_width, game_screen_height):
		pygame.display.set_mode((game_screen_width, game_screen_height)) # Изменяем размер окна
		screen_size = (game_screen_width, game_screen_height) # Обновляем переменную screen_size
	else:
		# Если размер не меняется, просто обновляем screen_size
		screen_size = current_window_size
	# --- Конец Расчет размеров окна с HUD ---


	# set the continue flag
	carryOn = True

	# set the clock (how fast the screen updates)
	clock = pygame.time.Clock()

	# have a black background
	screen.fill(BLACK)

	# initialize the grid for the maze
	grid = create_grid(grid_size)

	# create the maze using the grid - ИНИЦИАЛИЗИРУЕМ ДО УСЛОВИЙ РЕЖИМОВ
	maze = create_maze(grid, (grid_size//2,grid_size//2)) # use the starting vertex to be middle of the map

	# get all of the vertices in the maze
	vertices = maze.get_vertices() # Теперь maze существует здесь

	# draw the maze
	draw_maze(screen, maze, grid_size, WHITE, side_length, border_width, offset_x) # Передаем offset_x

	# initialize starting point of character and potential character 2
	start_point = (0,0)
	# opposing corner
	start_point2 = (grid_size-1,grid_size-1)
	# set end-point for the maze
	end_point = (grid_size-1,grid_size-1)
	# initialize opponent's end-point for two player mode
	end_point2 = (0,0)

	# randomize a start and end point
	choice = random.randrange(4)
	if choice == 0:
		start_point = (grid_size-1,grid_size-1)
		start_point2 = (0,0)
		end_point = (0,0)
		end_point2 = (grid_size-1,grid_size-1)
	elif choice == 1:
		start_point = (0,grid_size-1)
		start_point2 = (grid_size-1,0)
		end_point = (grid_size-1,0)
		end_point2 = (0,grid_size-1)
	elif choice == 2:
		start_point = (grid_size-1,0)
		start_point2 = (0,grid_size-1)
		end_point = (0,grid_size-1)
		end_point2 = (grid_size-1,0)
	# initialize winner variable
	winner = 0

	# initialize the character
	player1 = Character(screen, side_length, border_width, vertices,\
						start_point, end_point, start_point, GREEN, WHITE)

	# if the two player game mode is selected, initialize the other character
	if mode == 1:
		player2 = Character(screen, side_length, border_width, vertices,\
							start_point2, end_point2, start_point2, BLUE, WHITE)
	# if computer race mode is selected
	elif mode == 2:
		# initialize computer character
		computer_character = Character(screen, side_length, border_width, vertices,\
								 start_point2, end_point2, start_point2, GRAY, WHITE)
		# find the shortest path for the computer to get to the end sing astar
		path = astar.astar(start_point2, end_point2, maze)
		# initialize a queue to pop in edges to solve
		q = queue.Queue()
		# add the paths the computer has to take to the queue
		for edge in path:
			q.put(edge)
		# set the cooldown for how fast the computer moves (scales with maze size)
		computer_cooldown = grid_size*15
		# set the maximum cooldown for the computer
		if computer_cooldown > 350:
			computer_cooldown = 350
		# initialize timer
		computer_timer = pygame.time.get_ticks()
	# if computer chase mode is selected
	elif mode == 3:
		# initialize computer character
		computer_character = Character(screen, side_length, border_width, vertices,\
								 start_point, end_point, start_point, GRAY, WHITE)
		# create a deque for the paths to the player
		dq = deque()
		# put start_point for the deque
		dq.append(start_point)
		# set the cooldown for how fast the computer moves
		computer_cooldown = grid_size*10
		# set the maximum cooldown for the computer
		if computer_cooldown > 300:
			computer_cooldown = 300
		# set the initial wait time for the computer
		initial_wait = 3000
		# initialize timers
		computer_timer = pygame.time.get_ticks()
		initial_wait_timer = pygame.time.get_ticks()
	# if escape mode is selected
	elif mode == 4:
		# set random key points (from 1 to grid_size-2)
		# 8 keys in total
		x_coords = random.sample(range(1,grid_size-1),8)
		y_coords = random.sample(range(1,grid_size-1),8)
		# initialize empty key list
		unlock_keys = []
		# append coordinates to the key list
		for i in range(8):
				unlock_keys.append((x_coords[i],y_coords[i]))
		# re-initialize character
		player1 = Character(screen, side_length, border_width, vertices, start_point,\
							end_point, start_point, GREEN, WHITE, True, unlock_keys, GOLD)
		# initialize computer character
		computer_character = Character(screen, side_length, border_width, vertices,\
								 start_point, end_point, start_point, GRAY, WHITE) # Исправлено на border_width
		# create a deque for the paths to the player
		dq = deque()
		# put start_point for the deque
		dq.append(start_point)
		# set the cooldown for how fast the computer moves
		computer_cooldown = grid_size*100
		# set the maximum cooldown for the computer
		if computer_cooldown > 3000:
			computer_cooldown = 3000
		# set the initial wait time for the computer
		initial_wait = 3000
		# initialize timers
		computer_timer = pygame.time.get_ticks()
		initial_wait_timer = pygame.time.get_ticks()


	# --- Монеты ---
	# Генерируем монеты
	# Количество монет можно регулировать, например, proportionalно размеру лабиринта
	num_coins = (grid_size * grid_size) // 10 # Пример: 10% от количества клеток
	# --- Конец Монеты ---

	# --- Подбираемые элементы времени ---
	# Количество ускорителей и замедлителей (можно регулировать)
	num_accelerators = (grid_size * grid_size) // 20 # Пример: 5%
	num_slowdowns = (grid_size * grid_size) // 20 # Пример: 5%

	# Исключаем стартовые и конечные точки, а также позиции ключей
	excluded_positions = [start_point, end_point]
	if mode == 1:
		excluded_positions.extend([start_point2, end_point2])
	if mode == 4 and player1.keys:
		excluded_positions.extend(player1.keys)

	# Генерируем доступные позиции для всех предметов (монеты, ускорители, замедлители), исключая уже занятые и исключенные
	available_item_positions = [v for v in vertices if v not in excluded_positions]

	# Выбираем случайные позиции для монет из доступных
	coin_positions = random.sample(available_item_positions, min(num_coins, len(available_item_positions)))

	# Обновляем доступные позиции, исключая позиции монет
	available_item_positions = [v for v in available_item_positions if v not in coin_positions]

	# Выбираем случайные позиции для ускорителей
	accelerator_positions = random.sample(available_item_positions, min(num_accelerators, len(available_item_positions)))

	# Обновляем доступные позиции, исключая позиции ускорителей
	available_item_positions = [v for v in available_item_positions if v not in accelerator_positions]

	# Выбираем случайные позиции для замедлителей
	slowdown_positions = random.sample(available_item_positions, min(num_slowdowns, len(available_item_positions)))


	# Значения изменения времени (в секундах)
	ACCELERATOR_VALUE = 5 # Уменьшает время на 5 секунд
	SLOWDOWN_VALUE = 5 # Увеличивает время на 5 секунд
	# --- Конец Подбираемые элементы времени ---


	# draw the end-point
	draw_position(screen, side_length, border_width, end_point, RED, offset_x) # Передаем offset_x

	# if two player mode, draw endpoints
	if mode == 1:
		draw_position(screen, side_length, border_width, end_point, GREEN, offset_x) # Передаем offset_x
		draw_position(screen, side_length, border_width, end_point2, BLUE, offset_x) # Передаем offset_x

	# if computer mode, draw gray endpoint for computer
	elif mode == 2:
		draw_position(screen, side_length, border_width, end_point, GREEN, offset_x) # Передаем offset_x
		draw_position(screen, side_length, border_width, end_point2, GRAY, offset_x) # Передаем offset_x

	# if escape mode, draw keys
	elif mode == 4:
		# player1.draw_keys() # Отрисовка ключей теперь происходит в основном цикле
		# update console
		update_console(screen, screen_size, side_length, screen_size[0]//grid_size, WHITE, BLACK, player1.get_keys_left(), player1.get_wallBreaks(), offset_x) # Передаем offset_x

	# update the screen
	pygame.display.flip()

	# set cooldown for key presses
	cooldown = 100
	# initialize the cooldown timer
	start_timer = pygame.time.get_ticks()
	# if the two player game mode is selected, initialize the cooldown timer for second player
	if mode == 1:
		start_timer2 = pygame.time.get_ticks()

	# initialize game timer for solo mode
	# game_start_time = 0 # Больше не нужен в этой роли
	elapsed_time = 0.0 # Время, прошедшее с начала игры (используем float для точности)
	last_time = time.time() # Запоминаем время последнего обновления

	# main loop
	while carryOn:
		# action (close screen)
		for event in pygame.event.get():# user did something
			if event.type == pygame.QUIT:
				carryOn = False
				mode = -1 # Возвращаем -1 для выхода из игры
			elif event.type == pygame.KEYDOWN:
				#Pressing the Esc Key will quit the game
				if event.key == pygame.K_ESCAPE:
					carryOn = False
					mode = -1 # Возвращаем -1 для выхода из игры

		# --- Обновление таймера ---
		if mode == 0: # Таймер работает только в одиночном режиме
			current_time = time.time()
			delta_time = current_time - last_time # Время, прошедшее с прошлого кадра
			elapsed_time += delta_time # Добавляем прошедшее время к общему
			last_time = current_time # Обновляем время последнего обновления
		# --- Конец Обновление таймера ---


		# get the pressed keys
		keys = pygame.key.get_pressed()

		# --- Сбор монет и предметов времени ---
		player1_pos = player1.get_current_position()
		# Проверяем сбор монет
		if player1_pos in coin_positions:
			player1.collect_coin() # Собираем монету
			coin_positions.remove(player1_pos) # Удаляем монету из списка
		# Проверяем сбор ускорителей
		if player1_pos in accelerator_positions:
			elapsed_time = max(0.0, elapsed_time - ACCELERATOR_VALUE) # Уменьшаем время
			accelerator_positions.remove(player1_pos)
		# Проверяем сбор замедлителей
		if player1_pos in slowdown_positions:
			elapsed_time += SLOWDOWN_VALUE # Увеличиваем время
			slowdown_positions.remove(player1_pos)

		# Логика сбора для Player 2, если существует (не влияет на таймер в Solo режиме)
		if mode == 1:
			player2_pos = player2.get_current_position()
			if player2_pos in coin_positions:
				player2.collect_coin()
				coin_positions.remove(player2_pos)
			# Можно добавить сбор предметов времени для Player 2 с соответствующим эффектом
			# if player2_pos in accelerator_positions: ...
			# if player2_pos in slowdown_positions: ...

		# Логика сбора для компьютера, если существует (опционально, не влияет на таймер в Solo режиме)
		if mode == 2 or mode == 3 or mode == 4:
			computer_pos = computer_character.get_current_position()
			if computer_pos in coin_positions:
				coin_positions.remove(computer_pos)
			# Можно добавить сбор предметов времени для компьютера (без эффекта на его "время")
			# if computer_pos in accelerator_positions: ...
			# if computer_pos in slowdown_positions: ...

		# --- Конец Сбор монет и предметов времени ---


		if (pygame.time.get_ticks() - start_timer > cooldown):
			# get the current point of character
			current_point = player1.get_current_position()
			# move character right
			if keys[pygame.K_RIGHT]:
				# check if the next point is in the maze
				if (current_point[0]+1,current_point[1]) in vertices:
					next_point = (current_point[0]+1,current_point[1])
					# check if the next point is connected by an edge
					if (maze.is_edge((current_point,next_point))):
						player1.move_character_smooth(next_point,5)
						# if the current mode is chase mode or escape mode
						if mode == 3:
							# update the shortest path for the computer to use
							dq = update_path(next_point, dq)
						elif mode == 4:
							dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
					else:
						# if it is escape mode
						if mode == 4:
							# if the player pressed the space key, break the wall in the direction they are moving in
							if keys[pygame.K_SPACE] and player1.get_wallBreaks() > 0:
								maze = break_wall(maze, current_point, next_point)
								# move the player to that point
								player1.move_character_smooth(next_point,5)
								# decrement the player's number of wallBreaks
								player1.use_wallBreak()
								# update the shortest path for the computer to use
								dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
				# restart cooldown timer
				start_timer = pygame.time.get_ticks()
			# move character left
			elif keys[pygame.K_LEFT]:
				if (current_point[0]-1,current_point[1]) in vertices:
					next_point = (current_point[0]-1, current_point[1])
					if (maze.is_edge((current_point,next_point))):
						player1.move_character_smooth(next_point,5)
						# if the current mode is chase mode or escape mode
						if mode == 3:
							dq = update_path(next_point, dq)
						elif mode == 4:
							dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
					else:
						# if it is escape mode
						if mode == 4:
							# if the player pressed the space key, break the wall in the direction they are moving in
							if keys[pygame.K_SPACE] and player1.get_wallBreaks() > 0:
								maze = break_wall(maze, current_point, next_point)
								# move the player to that point
								player1.move_character_smooth(next_point,5)
								# decrement the player's number of wallBreaks
								player1.use_wallBreak()
								# update the shortest path for the computer to use
								dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
				# restart cooldown timer
				start_timer = pygame.time.get_ticks()
			# move character up
			elif keys[pygame.K_UP]:
				if (current_point[0],current_point[1]-1) in vertices:
					next_point = (current_point[0], current_point[1]-1)
					if (maze.is_edge((current_point,next_point))):
						player1.move_character_smooth(next_point,5)
						# if the current mode is chase mode or escape mode
						if mode == 3:
							dq = update_path(next_point, dq)
						elif mode == 4:
							dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
					else:
						# if it is escape mode
						if mode == 4:
							# if the player pressed the space key, break the wall in the direction they are moving in
							if keys[pygame.K_SPACE] and player1.get_wallBreaks() > 0:
								maze = break_wall(maze, current_point, next_point)
								# move the player to that point
								player1.move_character_smooth(next_point,5)
								# decrement the player's number of wallBreaks
								player1.use_wallBreak()
								# update the shortest path for the computer to use
								dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
				# restart cooldown timer
				start_timer = pygame.time.get_ticks()
			# move character down
			elif keys[pygame.K_DOWN]:
				if (current_point[0],current_point[1]+1) in vertices:
					next_point = (current_point[0], current_point[1]+1)
					if (maze.is_edge((current_point,next_point))):
						player1.move_character_smooth(next_point,5)
						# if the current mode is chase mode or escape mode
						if mode == 3:
							dq = update_path(next_point, dq)
						elif mode == 4:
							dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
					else:
						# if it is escape mode
						if mode == 4:
							# if the player pressed the space key, break the wall in the direction they are moving in
							if keys[pygame.K_SPACE] and player1.get_wallBreaks() > 0:
								maze = break_wall(maze, current_point, next_point)
								# move the player to that point
								player1.move_character_smooth(next_point,5)
								# decrement the player's number of wallBreaks
								player1.use_wallBreak()
								# update the shortest path for the computer to use
								dq = update_path_a(computer_character.get_current_position(), next_point, maze, dq)
				# restart cooldown timer
				start_timer = pygame.time.get_ticks()


		# PLAYER 2 MOVEMENT HERE (if gamemode selected)
		if mode == 1:
			# update the start timer for player 2
			start_timer2 = playerTwo(player2, maze, vertices, cooldown, start_timer2)


		# computer movement for race mode
		elif mode == 2:
			if (pygame.time.get_ticks() - computer_timer > computer_cooldown):
				computer_character.move_character_smooth(q.get(),5)
				# reset the cooldown timer for computer
				computer_timer = pygame.time.get_ticks()


		# computer movement for chase mode and escape mode
		elif mode == 3 or mode == 4:
			if mode == 4:
				# increase the computer speed if got another 2 keys
				# Эта логика должна быть в runGame после сбора ключей
				# if player1.increase_computer_speed(): # Вызов из character.increase_computer_speed
				#	 computer_cooldown = computer_cooldown/2
				# --- Логика увеличения скорости компьютера при сборе ключей ---
				if player1.escape and player1.keys is not None:
					# Предполагая, что collected_keys обновляется в Character
					# Или нужно обновить collected_keys здесь после сбора ключа
					pass # Логика должна быть при сборе ключа
				# --- Конец Логика увеличения скорости компьютера при сборе ключей ---

				# update console
				update_console(screen, screen_size, side_length, screen_size[0]//grid_size, WHITE, BLACK, player1.get_keys_left(), player1.get_wallBreaks(), offset_x) # Передаем offset_x

			# update the wait condition
			waitCondition = pygame.time.get_ticks() - initial_wait_timer > initial_wait
			# check if the wait condition is met
			if (waitCondition):
				if (pygame.time.get_ticks() - computer_timer > computer_cooldown):
					# make sure that the deque is not empty
					if dq:
						computer_character.move_character_smooth(dq.popleft(),5)
					# reset the cooldown timer for computer
					computer_timer = pygame.time.get_ticks()


		# --- Отрисовка всех элементов ---
		# Перерисовываем фон (включая область HUD)
		screen.fill(BLACK)
		# Заливаем фон HUD панели
		hud_rect = pygame.Rect(0, 0, hud_width, game_screen_height)
		pygame.draw.rect(screen, HUD_BG_COLOR, hud_rect)


		# Отрисовываем лабиринт
		draw_maze(screen, maze, grid_size, WHITE, side_length, border_width, offset_x) # Передаем offset_x

		# Отрисовываем оставшиеся монеты
		for coin_pos in coin_positions:
			draw_coin(screen, coin_image, coin_pos, side_length, border_width, offset_x)

		# Отрисовываем оставшиеся ускорители
		for acc_pos in accelerator_positions:
			draw_coin(screen, acc_image, acc_pos, side_length, border_width, offset_x)

		# Отрисовываем оставшиеся замедлители
		for slow_pos in slowdown_positions:
			draw_coin(screen, slow_image, slow_pos, side_length, border_width, offset_x)
		# Отрисовка персонажей и конечных точек (после всех предметов)
		draw_position(screen, side_length, border_width, end_point, RED, offset_x) # Передаем offset_x
		if mode == 1:
			draw_position(screen, side_length, border_width, end_point, GREEN, offset_x) # Передаем offset_x
			draw_position(screen, side_length, border_width, end_point2, BLUE, offset_x) # Передаем offset_x
			player2.draw_position(offset_x) # Передаем offset_x при отрисовке Player 2
		elif mode == 2:
			draw_position(screen, side_length, border_width, end_point, GREEN, offset_x) # Передаем offset_x
			draw_position(screen, side_length, border_width, end_point2, GRAY, offset_x) # Передаем offset_x
			computer_character.draw_position(offset_x) # Передаем offset_x при отрисовке компьютера
		elif mode == 3 or mode == 4:
			if mode == 4:
				player1.draw_keys(offset_x) # Передаем offset_x при отрисовке ключей
				if player1.collected_all(): # Проверяем разблокировку выхода
					draw_position(screen, side_length, border_width, end_point, GREEN, offset_x) # Передаем offset_x
				else:
					draw_position(screen, side_length, border_width, end_point, RED, offset_x) # Передаем offset_x
				# update console
				update_console(screen, screen_size, side_length, screen_size[0]//grid_size, WHITE, BLACK, player1.get_keys_left(), player1.get_wallBreaks(), offset_x) # Передаем offset_x


			if waitCondition:
				computer_character.draw_position(offset_x) # Передаем offset_x при отрисовке компьютера, если он активен

		player1.draw_position(offset_x) # Передаем offset_x при отрисовке игрока
		# --- Конец Отрисовка всех элементов ---


		# --- Отрисовка HUD панели (таймер и монеты) ---
		# Область HUD панели уже залита черным фоном
		# Текст с количеством монет
		coin_text = f"Монеты: {player1.get_coins()}"
		font_size_coins = hud_width // 8 # Размер шрифта для монет пропорционально ширине HUD
		font_coins = pygame.font.SysFont("ubuntu", font_size_coins)
		text_surface_coins = font_coins.render(coin_text, True, GOLD) # Цвет текста монет
		text_rect_coins = text_surface_coins.get_rect(midtop=(hud_width // 2, 20)) # Позиция в середине HUD, небольшой отступ сверху

		screen.blit(text_surface_coins, text_rect_coins)


		# Текст с таймером (только в Solo режиме)
		if mode == 0:
			timer_text = f"Время: {elapsed_time:.2f} сек" # Отображаем время с двумя знаками после запятой
			font_size_timer = hud_width // 7 # Размер шрифта для таймера (чуть больше)
			font_timer = pygame.font.SysFont("ubuntu", font_size_timer)
			text_surface_timer = font_timer.render(timer_text, True, WHITE) # Цвет текста таймера
			text_rect_timer = text_surface_timer.get_rect(midtop=(hud_width // 2, 70)) # Позиция ниже монет

			screen.blit(text_surface_timer, text_rect_timer)

		# --- Конец Отрисовка HUD панели ---


		# Обновляем весь экран в конце цикла
		pygame.display.flip()


		# win conditions for the different modes
		if mode == 0:
			if player1.reached_goal():
				carryOn = False

		elif mode == 1:
			if player1.reached_goal():
				winner = 1
				carryOn = False
			elif player2.reached_goal():
				winner = 2
				carryOn = False

		elif mode == 2:
			if player1.reached_goal():
				winner = 1
				carryOn = False
			elif computer_character.reached_goal():
				winner = 2
				carryOn = False

		elif mode == 3:
			if player1.reached_goal():
				winner = 1
				carryOn = False
			elif computer_character.get_current_position() == player1.get_current_position() and waitCondition:
				winner = 2
				carryOn = False

		elif mode == 4:
			if player1.escaped():
				winner = 1
				carryOn = False
			elif computer_character.get_current_position() == player1.get_current_position() and waitCondition:
				winner = 2
				carryOn = False


		# limit to 60 frames per second (fps)
		clock.tick(60) # Ограничиваем FPS для стабильности

	# stop the game engine once exited the game
	# pygame.quit() # Не вызываем здесь, закрываем в main

	# solo mode
	if mode == 0:
		# При завершении игры в соло режиме возвращаем elapsed_time
		final_time = elapsed_time
		# Добавляем результат в таблицу лидеров: время и монеты
		add_score_to_leaderboard(final_time, player1.get_coins(), "Solo Player") # Передаем количество монет
		# Возвращаем режим и время
		return mode, final_time # Возвращаем final_time
	# other modes
	else:
		# Возвращаем режим и победителя
		return mode, winner

# main function
if __name__ == "__main__":
	# initialize the game engine ONCE
	pygame.init()

	# set the window display position
	set_window_position(50,50)

	# initialize states
	states = {0:"Main Menu", 1:"Gameplay", 2:"Leaderboard", 3:"End Game"} # Добавили состояние для экрана окончания игры
	current_state = states[0]
	# initialize variables
	grid_size = 20 # Дефольные значения
	side_length = 10 # Дефольные значения
	mode = 0 # Дефольный режим

	# Флаг для главного цикла
	Run = True

	# Создаем поверхность экрана один раз в начале
	screen_size = (800, 600) # Дефольный размер окна для меню и таблицы лидеров
	screen = pygame.display.set_mode(screen_size)
	fon = load_background(screen)
	screen.blit(fon, (0, 0))

	while Run:
		if current_state == states[0]: # Главное меню
			# startScreen теперь возвращает Run, grid_size, side_length, mode, next_state
			Run, grid_size, side_length, mode, next_state = ui_file.startScreen(screen, screen_size) # Передаем screen и screen_size
			if next_state != -1: # Если это не выход из игры
				current_state = states[next_state] # Переходим в следующее состояние
			else:
				Run = False # Выходим из главного цикла

		elif current_state == states[1]: # Состояние игры
			# runGame сам устанавливает размер окна, но он должен использовать переданную поверхность
			# В Solo режиме runGame вернет final_time, в других режимах - winner
			game_result = runGame(screen, screen_size, grid_size, side_length, mode) # Передаем screen, screen_size, grid_size, side_length, mode
			# После игры переходим в состояние окончания игры
			current_state = states[3]
			end_game_info = (mode, game_result[1]) # Сохраняем информацию для endGame (режим и результат - время или победитель)

		elif current_state == states[2]: # Состояние таблицы лидеров
			# Перед показом таблицы лидеров убедимся, что размер окна соответствует меню
			pygame.display.set_mode(screen_size)
			next_state = ui_file.leaderboardScreen(screen, screen_size) # Передаем screen и screen_size
			if next_state == -1: # Если leaderboardScreen вернул -1 (сигнал выхода)
				Run = False # Завершаем главный цикл
			else:
				current_state = states[next_state] # Иначе переходим в состояние, которое вернула leaderboardScreen (0 - главное меню)

		elif current_state == states[3]: # Состояние окончания игры
			# Перед показом экрана окончания игры убедимся, что размер окна соответствует меню
			pygame.display.set_mode(screen_size)
			# Передаем режим и результат (время или победитель)
			ui_file.endGame(end_game_info[0], end_game_info[1]) # Вызываем endGame с сохраненными данными
			current_state = states[0] # После экрана окончания игры возвращаемся в главное меню


	# Закрываем Pygame один раз при полном выходе
	pygame.quit()