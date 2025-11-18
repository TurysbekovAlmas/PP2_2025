import pygame
from random import randrange, choice
import time

Res = 600
size = 25
sizea = 15
score = 0
speed = 3

x, y = randrange(0, Res, size), randrange(0, Res, size)
apple = randrange(0, Res, size), randrange(0, Res, size)

length = 1
snake = [(x, y)]

dx, dy = 0, 0
FPS = 10

pygame.init()
sc = pygame.display.set_mode([Res, Res])
clock = pygame.time.Clock()
font_score = pygame.font.SysFont('Arial', 26, bold=True)
font_end = pygame.font.SysFont('Arial', 50, bold=True)

food_timer = time.time()
food_duration = 5  # in seconds
food_weight = {1: 'light', 2: 'medium', 3: 'heavy'}  # Different weights for food items

# Obstacles for each level
obstacles = {
    1: [(200, 200), (300, 400), (400, 100)],
    2: [(100, 300), (500, 200), (200, 400)],
    3: [(150, 100), (400, 300), (100, 500)]
}

# Bonus points with different colors and disappearing times
bonus_points = {
    (400, 200): (pygame.Color('blue'), 5),   # Blue bonus point lasts for 5 seconds
    (100, 400): (pygame.Color('yellow'), 3), # Yellow bonus point lasts for 3 seconds
    (500, 500): (pygame.Color('purple'), 7)  # Purple bonus point lasts for 7 seconds
}

level = 1

while True:
    sc.fill(pygame.Color('black'))
    
    # Draw obstacles for the current level
    for obstacle in obstacles[level]:
        pygame.draw.rect(sc, pygame.Color('gray'), (*obstacle, size, size))
    
    # Draw bonus points
    for point, (color, _) in bonus_points.items():
        pygame.draw.rect(sc, color, (*point, sizea, sizea))
    
    [(pygame.draw.rect(sc, pygame.Color('green'), (i, j, size, size))) for i, j in snake]
    pygame.draw.rect(sc, pygame.Color('red'), (*apple, size, size))

    render_score = font_score.render(f'SCORE: {score}', 1, pygame.Color('orange'))
    sc.blit(render_score, (5, 5))

    x += dx * size
    y += dy * size
    snake.append((x, y))
    snake = snake[-length:]

    # Check for collision with obstacles
    if any((x, y) == obstacle for obstacle in obstacles[level]):
        while True:
            render_end = font_end.render('GAME OVER', 1, pygame.Color('orange'))
            sc.blit(render_end, (Res // 2 - 150, Res // 3))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
    
    # Check for collision with bonus points and handle their disappearance
    for point, (color, duration) in bonus_points.items():
        if (x, y) == point:
            score += 5  # Increment score for collecting bonus points
            del bonus_points[point]
            break  # Only allow collecting one bonus point at a time
    
    # Check for time expiration of bonus points
    expired_points = [point for point, (_, duration) in bonus_points.items() if time.time() - food_timer > duration]
    for point in expired_points:
        del bonus_points[point]
    
    if snake[-1] == apple:
        score += 1
        apple = randrange(0, Res, size), randrange(0, Res, size)
        length += 1
        FPS += 0.5
        food_timer = time.time()
        
        # Add more obstacles when certain score thresholds are reached
        if score == 10 or score == 20 or score == 30 or score == 40:
            if level < 3:
                level += 1

    if time.time() - food_timer > food_duration:
        apple = randrange(0, Res, size), randrange(0, Res, size)
        food_timer = time.time()

    if x < 0 or x > Res - size or y < 0 or y > Res - size or len(snake) != len(set(snake)):
        while True:
            render_end = font_end.render('GAME OVER', 1, pygame.Color('orange'))
            sc.blit(render_end, (Res // 2 - 150, Res // 3))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    key = pygame.key.get_pressed()
    if key[pygame.K_UP]:
        dx, dy = 0, -1
    if key[pygame.K_DOWN]:
        dx, dy = 0, 1
    if key[pygame.K_LEFT]:
        dx, dy = -1, 0
    if key[pygame.K_RIGHT]:
        dx, dy = 1, 0
