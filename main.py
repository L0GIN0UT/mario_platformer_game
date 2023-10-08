import os
import pickle

import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import re

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Платформер')

# Текст
font = pygame.font.Font("fonts/hello-world.ttf", 70)
font_score = pygame.font.Font("fonts/hello-world.ttf", 35)

def count_levels():
    folder_path = "levels"
    counter = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            match = re.match(r"level\d+_data", file)
            if match:
                counter += 1
    return counter

# Цвета
white = (255, 255, 255)
green = (0, 255, 128)
red = (255, 0, 0)

# Изображения
jump = pygame.transform.scale(pygame.image.load("img/mario_jump.png"), (55, 65))
bg = pygame.image.load("img/bg.png")
restart_img = pygame.image.load("img/restart_btn.png")
start_img = pygame.image.load("img/start_btn.png")
exit_img = pygame.image.load("img/exit_btn.png")
score_bar = pygame.transform.scale(pygame.image.load("img/score_bar.png"), (180, 90))
exit_btn_img = pygame.transform.scale(pygame.image.load("img/exit_btn.png"), (90, 45))


# Звуки
pygame.mixer.music.load("sounds/saund.mp3")
pygame.mixer.music.play()
coin_fx = pygame.mixer.Sound("sounds/collect_coin.mp3")
coin_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound("sounds/mario_death.mp3")
jump_fx = pygame.mixer.Sound("sounds/mario_jump.mp3")
nextLVL_fx = pygame.mixer.Sound("sounds/nextLVL.mp3")
win_fx = pygame.mixer.Sound("sounds/win.mp3")
win_fx.set_volume(0.2)


# Основные переменные
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_level = count_levels()
score = 0
temp = 0


# def draw_greed():
#     for line in range(0, 20):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_width))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))



def reset_level(level):
    player.restart(100, screen_height - 110)
    enemy_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()

    if path.exists(f"levels\level{level}_data"):
        pickle_in = open(f"levels\level{level}_data", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # Позиция мышки
        pos = pygame.mouse.get_pos()

        # проверка мыши и клика
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Отрисовка
        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.restart(x, y)

    def restart(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f"img/mario_{num}.png")
            img_right = pygame.transform.scale(img_right, (50, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.dead_image = pygame.image.load("img/mario_RIP.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 3
        col_thresh = 20

        if game_over == 0:

            # Нажатие клавиш
            key = pygame.key.get_pressed()

            if key[pygame.K_SPACE] and not self.jumped and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.direction = 1
                self.counter += 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    if key[pygame.K_SPACE]:
                        self.image = jump
                    else:
                        self.image = self.images_right[self.index]
                if self.direction == -1:
                    if key[pygame.K_SPACE]:
                        self.image = pygame.transform.flip(jump, True, False)
                    else:
                        self.image = self.images_left[self.index]

            # Анимация
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    if key[pygame.K_SPACE]:
                        self.image = jump
                    else:
                        self.image = self.images_right[self.index]
                if self.direction == -1:
                    if key[pygame.K_SPACE]:
                        self.image = pygame.transform.flip(jump, True, False)
                    else:
                        self.image = self.images_left[self.index]

            # Гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Проверка на стлокновение
            self.in_air = True
            for tile in world.tile_list:
                # проверка на столкновении по x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # проверка на столкновении по y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверка под землей
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # проверка над землей
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Столкновение с врагом
            if pygame.sprite.spritecollide(self, enemy_group, False):
                pygame.mixer.music.pause()
                death_fx.play()
                game_over = -1


            # Столкновение с платформой
            for platform in platform_group:
                t = 0
                # по координате х
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # по координате y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # если под
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # если над
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # движение с платформой
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # dy = platform.rect.bottom - self.rect.top + 1

            # Столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                pygame.mixer.music.pause()
                death_fx.play()
                game_over = -1

            # Столкновение с дверью
            if pygame.sprite.spritecollide(self, exit_group, False):
                nextLVL_fx.play()
                game_over = 1

            # Ставим персонажа на место
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = pygame.transform.scale(self.dead_image, (50, 60))
            draw_text("GAME OVER!", font, red, (screen_width // 2) - 140, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y += 2

        # Отрисовка персонажа
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over


class World():
    def __init__(self, data):
        self.tile_list = []

        block = pygame.image.load("img/dark_block.png")
        grass = pygame.image.load("img/gold_block.png")

        row_count = 0
        for row in data:
            col_count = 0
            for title in row:
                if title == 1:
                    img = pygame.transform.scale(block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if title == 2:
                    img = pygame.transform.scale(grass, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if title == 3:
                    enemy = Enemy(col_count * tile_size + 5, row_count * tile_size + 10)
                    enemy_group.add(enemy)
                if title == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if title == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if title == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if title == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2) + 3, row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if title == 8:
                    exit = Exit(col_count * tile_size - (tile_size // 2), row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("img/platform.png"), (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 100:
            self.move_direction *= -1
            self.move_counter *= -1



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("img/gumba.png"), (tile_size - 10, tile_size - 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.counter += 1
        if abs(self.counter) > 50:
            self.move_direction *= -1
            self.counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("img/lava.gif"), (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("img/coin.png"),
                                            (int(tile_size // 2), int(tile_size // 1.5)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("img/exit.png"),
                                            (int(tile_size * 1.5), int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 110)

enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

score_coin = Coin(tile_size // 2, tile_size // 2)



# Загрузка и сохранение мира
if path.exists(f"levels\level{level}_data"):
    pickle_in = open(f"levels\level{level}_data", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)

start_button = Button((screen_width // 2) - 350, (screen_height // 2) + 50, start_img)
exit_button = Button((screen_width // 2) + 150, (screen_height // 2) + 50, exit_img)
restart_button = Button((screen_width // 2) - 50, (screen_height // 2) + 100, restart_img)

run = True
while run:

    clock.tick(fps)
    screen.blit(bg, (0, 0))

    if main_menu:
        screen.blit(pygame.image.load("img/title.png"), (0, 0))
        screen.blit(pygame.image.load("img/mario_1.png"), (100, 875))
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            run = False

    else:
        world.draw()

        if game_over == 0:
            enemy_group.update()
            platform_group.update()

            # Столкновение с монеткой
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_fx.play()
                score += 1
            screen.blit(score_bar, (tile_size//4 - 52, tile_size//4 - 28))
            draw_text("x " + str(score), font_score, white, tile_size//2 + 20, tile_size//4 - 7)
            coin_group.add(score_coin)

        enemy_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        if game_over == -1:
            coin_group.empty()
            exit_button = Button(screen_width // 2 - 35, screen_height // 2 + 180, exit_btn_img)
            if restart_button.draw():
                death_fx.stop()
                pygame.mixer.music.unpause()
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
            if exit_button.draw():
                run = False
        if game_over == 1:
            coin_fx.stop()
            coin_group.empty()
            level += 1
            if level <= max_level:
                world_data = []
                world = reset_level(level)
                game_over = 0
            if level == max_level + 1:
                nextLVL_fx.stop()
                pygame.mixer.music.stop()
                win_fx.play()
            else:
                draw_text("YOU WIN!", font, green, (screen_width // 2) - 100, (screen_height // 2) - 100)
                draw_text(f"score: {score}", font, white, (screen_width // 2) - 100, (screen_height // 2) - 10)
                exit_button = Button(screen_width // 2 - 35, screen_height // 2 + 180, exit_btn_img)
                if restart_button.draw():
                    win_fx.stop()
                    pygame.mixer.music.play()
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                if exit_button.draw():
                    run = False



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
