import pygame
import sys
import random
import psycopg2 as ps

# ------------------ Настройки БД ------------------
conn = ps.connect(
    host='localhost',
    dbname='postgres',
    user='postgres',
    password='MyNewPassword123!',
    port=5432
)
cur = conn.cursor()

# ------------------ Создание таблиц ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS user_score (
    score_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    score INT DEFAULT 0,
    level INT DEFAULT 1
);
""")
conn.commit()

# ------------------ Игровые настройки ------------------
SIZE_BLOCK = 20
COUNT_BLOCKS = 20
HEADER_MARGIN = 50

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)

pygame.init()
screen_size = [SIZE_BLOCK*COUNT_BLOCKS, SIZE_BLOCK*COUNT_BLOCKS+HEADER_MARGIN]
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
font = pygame.font.SysFont('courier', 24)

# ------------------ Пользователь ------------------
username = input("Enter your username: ")

# Проверяем, есть ли пользователь
cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
res = cur.fetchone()
if res:
    user_id = res[0]
    cur.execute("SELECT score, level FROM user_score WHERE user_id=%s", (user_id,))
    score_data = cur.fetchone()
    if score_data:
        total_score, level = score_data
    else:
        total_score, level = 0, 1
else:
    cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (username,))
    user_id = cur.fetchone()[0]
    cur.execute("INSERT INTO user_score (user_id) VALUES (%s)", (user_id,))
    total_score, level = 0, 1
conn.commit()

print(f"Welcome {username}! Level: {level}, Score: {total_score}")

# ------------------ Классы ------------------
class SnakeBlock:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x==other.x and self.y==other.y

def draw_block(color, block):
    pygame.draw.rect(screen, color,
                     [block.x*SIZE_BLOCK, HEADER_MARGIN+block.y*SIZE_BLOCK, SIZE_BLOCK, SIZE_BLOCK])

# ------------------ Функции ------------------
def save_progress():
    cur.execute("SELECT score_id FROM user_score WHERE user_id=%s", (user_id,))
    score_id = cur.fetchone()[0]
    cur.execute("UPDATE user_score SET score=%s, level=%s WHERE score_id=%s",
                (total_score, level, score_id))
    conn.commit()
    print("Progress saved!")

def get_random_empty_block(snake_blocks):
    while True:
        block = SnakeBlock(random.randint(0, COUNT_BLOCKS-1), random.randint(0, COUNT_BLOCKS-1))
        if block not in snake_blocks:
            return block

# ------------------ Основная игра ------------------
def play_game():
    global total_score, level
    snake = [SnakeBlock(5,5), SnakeBlock(5,6), SnakeBlock(5,7)]
    direction = (0,1)
    apple = get_random_empty_block(snake)
    speed = 5 + level*2
    running = True
    pause = False

    while running:
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, [0,0,screen_size[0], HEADER_MARGIN])
        score_text = font.render(f"Score: {total_score} Level: {level}", True, BLACK)
        screen.blit(score_text, (10,10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = not pause
                if not pause:
                    if event.key == pygame.K_UP and direction!=(0,1):
                        direction = (0,-1)
                    elif event.key == pygame.K_DOWN and direction!=(0,-1):
                        direction = (0,1)
                    elif event.key == pygame.K_LEFT and direction!=(1,0):
                        direction = (-1,0)
                    elif event.key == pygame.K_RIGHT and direction!=(-1,0):
                        direction = (1,0)

        if pause:
            pause_text = font.render("PAUSED", True, RED)
            screen.blit(pause_text, (screen_size[0]//2-50, screen_size[1]//2))
            pygame.display.flip()
            clock.tick(5)
            continue

        head = snake[-1]
        new_head = SnakeBlock(head.x + direction[0], head.y + direction[1])

        # Проверка столкновения
        if new_head in snake or not (0<=new_head.x<COUNT_BLOCKS and 0<=new_head.y<COUNT_BLOCKS):
            print("Game over!")
            save_progress()
            return

        snake.append(new_head)
        if new_head == apple:
            total_score += 10
            apple = get_random_empty_block(snake)
        else:
            snake.pop(0)

        # Рисуем яблоки и змейку
        draw_block(RED, apple)
        for block in snake:
            draw_block(GREEN, block)

        pygame.display.flip()
        clock.tick(speed)

# ------------------ Запуск игры ------------------
play_game()
cur.close()
conn.close()
