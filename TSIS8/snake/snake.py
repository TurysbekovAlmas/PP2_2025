import pygame
from random import randrange


Res=600
size=25
sizea=15
score=0
speed=3

x,y=randrange(0, Res, size),randrange(0, Res, size)
apple=randrange(0, Res, size),randrange(0, Res, size)

length=1
snake=[(x,y)]

dx, dy=0,0
FPS=10

pygame.init()
sc=pygame.display.set_mode([Res, Res])
clock=pygame.time.Clock()
font_score = pygame.font.SysFont('Arial', 26, bold=True)
font_end = pygame.font.SysFont('Arial', 50, bold=True)


while True:
    sc.fill(pygame.Color('black'))
    [(pygame.draw.rect(sc, pygame.Color('green'), (i, j, size, size))) for i, j in snake ]
    pygame.draw.rect(sc, pygame.Color('red'), (*apple, size, size))
    
    render_score=font_score.render(f'SCORE: {score}', 1, pygame.Color('orange'))
    sc.blit(render_score,(5, 5))
    
    x += dx*size
    y += dy*size
    snake.append((x,y))
    snake=snake[-length:]
    
    if snake[-1]==apple:
        apple=randrange(0, Res, size),randrange(0, Res, size)
        length+=1
        FPS+=0.5
        score+=1

    if x<0 or x> Res-size or y<0 or y> Res-size or len(snake) != len(set(snake)):
        while True:
            render_end=font_end.render('GAME OVER', 1, pygame.Color('orange'))
            sc.blit(render_end,(Res//2-150, Res//3))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    exit()
    pygame.display.flip()
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            exit()
    key=pygame.key.get_pressed()
    if key[pygame.K_UP]:
        dx, dy=0, -1
    if key[pygame.K_DOWN]:
        dx, dy=0, 1
    if key[pygame.K_LEFT]:
        dx, dy=-1, 0
    if key[pygame.K_RIGHT]:
        dx, dy=1, 0       