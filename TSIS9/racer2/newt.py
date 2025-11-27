import pygame
import sys

pygame.init()
W, H = 600, 800
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 28)
pygame.display.set_caption("Coin Drop Game")
# Player
PW, PH = 80, 18
player_x = W // 2 - PW // 2
player_y = 12
PLAYER_SPEED = 6

# Floor
FLOOR_H = 40
floor_y = H - FLOOR_H

# Coins
coins = []  # active falling coins: dicts with x,y,vy,r
COLLECTED = 0
COLLECTED_LIST = []  # for drawing collected coin icons
GRAVITY = 0.45
COIN_R = 9

def drop_coin():
    coins.append({"x": player_x + PW // 2, "y": player_y + PH + COIN_R, "vy": 0.0, "r": COIN_R})

def draw_floor():
    pygame.draw.rect(screen, (30, 30, 30), (0, floor_y, W, FLOOR_H))

def draw_player():
    pygame.draw.rect(screen, (50, 150, 250), (player_x, player_y, PW, PH))

def draw_active_coins():
    for c in coins:
        pygame.draw.circle(screen, (255, 215, 0), (int(c["x"]), int(c["y"])), c["r"])

def update_coins():
    global COLLECTED
    to_remove = []
    for i, c in enumerate(coins):
        c["vy"] += GRAVITY
        c["y"] += c["vy"]
        # floor collision -> collect and remove
        if c["y"] + c["r"] >= floor_y:
            COLLECTED += 1
            COLLECTED_LIST.append(1)  # placeholder to visualize a coin
            to_remove.append(i)
    # remove collected coins
    for i in reversed(to_remove):
        coins.pop(i)

def draw_collected_icons():
    # Draw collected coins as a row of small circles in top-left
    sx, sy = 8, 48
    gap = 18
    cols = 20
    for idx in range(len(COLLECTED_LIST)):
        cx = sx + (idx % cols) * gap
        cy = sy + (idx // cols) * gap
        pygame.draw.circle(screen, (255, 215, 0), (cx, cy), 7)
        pygame.draw.circle(screen, (200, 140, 0), (cx, cy), 7, 2)

def draw_score():
    txt = FONT.render(f"Collected: {COLLECTED}", True, (240,240,240))
    screen.blit(txt, (8, 8))

def main():
    global player_x
    running = True
    while running:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    drop_coin()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += PLAYER_SPEED
        # clamp player
        player_x = max(0, min(W - PW, player_x))

        update_coins()

        screen.fill((18, 18, 30))
        draw_player()
        draw_active_coins()
        draw_floor()
        draw_score()
        draw_collected_icons()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()