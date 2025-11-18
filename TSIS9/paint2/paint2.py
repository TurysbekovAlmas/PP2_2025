import pygame
import math

white = (255, 255, 255)
eraser = (0, 0, 0)
green = (34, 139, 34)
blue = (0, 0, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
orange = (255, 165, 0)
purple = (128, 0, 128)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()

    radius = 2
    mode = white
    last_pos = None

    while True:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                # determine if a letter key was pressed
                if event.key == pygame.K_r:
                    mode = red
                elif event.key == pygame.K_g:
                    mode = green
                elif event.key == pygame.K_b:
                    mode = blue
                elif event.key == pygame.K_y:
                    mode = yellow
                elif event.key == pygame.K_w:
                    mode = white
                elif event.key == pygame.K_o:
                    mode = orange
                elif event.key == pygame.K_p:
                    mode = purple
                elif event.key == pygame.K_x:    
                    drawRectangle(screen, pygame.mouse.get_pos(), 200, 100, mode)
                elif event.key == pygame.K_c:
                    drawCircle(screen, pygame.mouse.get_pos(), mode)
                elif event.key == pygame.K_s:
                    drawSquare(screen, pygame.mouse.get_pos(), 200, mode)
                elif event.key == pygame.K_t:
                    drawRightTriangle(screen, pygame.mouse.get_pos(), 200, 100, mode)
                elif event.key == pygame.K_a:
                    drawEquilateralTriangle(screen, pygame.mouse.get_pos(), 200, mode)
                elif event.key == pygame.K_d:
                    drawRhombus(screen, pygame.mouse.get_pos(), 100, 150, mode)
                if event.key == pygame.K_BACKSPACE:
                    radius = 20
                    mode = eraser
                else:
                    radius = 2

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # start a new line
                last_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                # draw a line from the last point to the current point
                if last_pos is not None:
                    start_pos = last_pos
                    end_pos = pygame.mouse.get_pos()
                    drawLineBetween(screen, start_pos, end_pos, radius, mode)
                    last_pos = end_pos

        pygame.display.flip()
        clock.tick(60)


def drawLineBetween(screen, start, end, width, color_mode):
    c1 = max(0, min(255, 2 * start[0] - 256))
    c2 = max(0, min(255, 2 * start[1]))

    color = color_mode
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    for i in range(iterations):
        progress = 1.0 * i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)

# Фигуры
def drawRectangle(screen, mouse_pos, w, h, color):
    x = mouse_pos[0]
    y = mouse_pos[1]
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect, 4)  # 4th parameter is outline of the rectangle


def drawCircle(screen, mouse_pos, color):
    x = mouse_pos[0]
    y = mouse_pos[1]
    pygame.draw.circle(screen, color, (x, y), 100, 5)  # 4th parameter is outline of the circle


def drawSquare(screen, mouse_pos, side_length, color):
    x = mouse_pos[0]
    y = mouse_pos[1]
    rect = pygame.Rect(x, y, side_length, side_length)
    pygame.draw.rect(screen, color, rect, 4)


def drawRightTriangle(screen, mouse_pos, width, height, color):
    x = mouse_pos[0]
    y = mouse_pos[1]
    points = [(x, y), (x + width, y), (x, y + height)]
    pygame.draw.polygon(screen, color, points, 4)


def drawEquilateralTriangle(screen, mouse_pos, side_length, color):
    x = mouse_pos[0]
    y = mouse_pos[1]
    height = side_length * math.sqrt(3) / 2
    points = [(x, y), (x + side_length, y), (x + side_length / 2, y + height)]
    pygame.draw.polygon(screen, color, points, 4)


def drawRhombus(screen, mouse_pos, width, height, color):
    x = mouse_pos[0]
    y = mouse_pos[1]
    points = [(x, y + height / 2), (x + width / 2, y), (x + width, y + height / 2), (x + width / 2, y + height)]
    pygame.draw.polygon(screen, color, points, 4)


main()