import pygame
import time

pygame.init()


"""setting up the color scheme for the game """

white = (255, 255, 255)
black = (0, 0, 0)


"""setting up the screen size"""

desktopWidth, desktopHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
pole_x_1 = 300
pole_x_2 = 600
pole_start = 100
pole_height = 350
display_width = 72 * int(desktopWidth/100)
display_height = 95 * int(desktopHeight/100)


"""setting the game-name and display window"""

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Hoaul')


pole = pygame.image.load('pole.png')
rod = pygame.image.load('rod.png')


clock = pygame.time.Clock()


def blit_poles():

    for i in xrange(pole_start, pole_start + pole_height):
        gameDisplay.blit(pole, (pole_x_1, i))
        gameDisplay.blit(pole, (pole_x_2, i))

def blit_rod(x_1, y_1, x_2, y_2):

    slope = float(y_2 - y_1) / (x_2 - x_1)

    for i in xrange(x_1, x_2):
        y = y_1 + slope * (i - x_1)
        gameDisplay.blit(rod, (i, y))



def game_loop():

    x_1 = pole_x_1
    x_2 = pole_x_2
    y_1 = pole_start + pole_height
    y_2 = pole_start + pole_height

    while True:

        gameDisplay.fill(white)
        blit_rod(x_1, y_1, x_2, y_2)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

                if event.key == pygame.K_w:
                    y_1 -= 10

                if event.key == pygame.K_s:
                    y_1 += 10

                if event.key == pygame.K_UP:
                    y_2 -= 10

                if event.key == pygame.K_DOWN:
                    y_2 += 10


                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        blit_poles()
        pygame.display.update()


game_loop()
pygame.quit()
quit()
