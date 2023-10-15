import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 50
cols = 20
margin = 100
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Создатель Уровней')


#load images
bg_img = pygame.image.load('img/bg.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
block_img = pygame.image.load('img/dark_block.png')
gold_block_img = pygame.image.load('img/gold_block.png')
enemy_img = pygame.image.load('img/gumba.png')
platform_x_img = pygame.image.load('img/platform_x.png')
platform_y_img = pygame.image.load('img/platform_y.png')
lava_img = pygame.image.load('img/lava.gif')
coin_img = pygame.image.load('img/coin.png')
exit_img = pygame.image.load('img/exit.png')
save_img = pygame.image.load('img/save_btn.png')
load_img = pygame.image.load('img/load_btn.png')
exit_button = pygame.image.load('img/exit_btn.png')


# Переменные
clicked = False
level = 1

# Цвета
white = (255, 255, 255)
black = (0, 0, 0)

font = pygame.font.SysFont('Futura', 24)

# Создание пустого мира
world_data = []
for row in range(20):
	r = [0] * 20
	world_data.append(r)

# Создание границ
for tile in range(0, 20):
	world_data[19][tile] = 2
	world_data[0][tile] = 1
	world_data[tile][0] = 1
	world_data[tile][19] = 1

# Вывод текста на экран
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(21):
		# Вертикальные линии
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		# Горизонтальные линии
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(20):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					# Барьер
					img = pygame.transform.scale(block_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					# Блок
					img = pygame.transform.scale(gold_block_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					# Враг
					img = pygame.transform.scale(enemy_img, (tile_size, int(tile_size * 0.75)))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 4:
					# Платформа х
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					# Платформа у
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					# Лава
					img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				if world_data[row][col] == 7:
					# Монетка
					img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 8:
					# Выход
					img = pygame.transform.scale(exit_img, (int(tile_size * 1.5), int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		# Получение позиции мышки
		pos = pygame.mouse.get_pos()

		# Проверка на нажатии мышки
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		# Отрисовка камеры
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

# Создание кнопог Сохранение и Загрузка
save_button = Button(screen_width // 2 - 50, screen_height - 80, save_img)
load_button = Button(screen_width // 2 + 150, screen_height - 80, load_img)
exit_button = Button(screen_width // 2 + 350, screen_height - 80, pygame.transform.scale(exit_button, (80, 42)))

# Основное
run = True
while run:

	clock.tick(fps)

	# Отрисока фона
	screen.fill(black)
	screen.blit(bg_img, (0, 0))


	# Загрузка и сохранение
	if save_button.draw():
		# Сохранение
		pickle_out = open(f'levels\level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		# Загрузка
		if path.exists(f'levels\level{level}_data'):
			pickle_in = open(f'levels\level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)
	if exit_button.draw():
		run = False

	# Отрисовка фона и мира
	draw_grid()
	draw_world()


	# Текст в мире
	draw_text(f'Уровень: {level}', font, white, tile_size, screen_height - 80)
	draw_text('Нажмите стрелку вверх или', font, white, tile_size, screen_height - 60)
	draw_text('стрелку вниз чтобы сменить уровень', font, white, tile_size, screen_height - 40)

	# Обработка
	for event in pygame.event.get():
		# Выход
		if event.type == pygame.QUIT:
			run = False
		# Смена объектов
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			# Координаты в области плитки
			if x < 20 and y < 20:
				# Обновление значения плитки
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 8:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 8
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		# Вверх или Вниз для смены уровня
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	# Обновление экрана
	pygame.display.update()

pygame.quit()