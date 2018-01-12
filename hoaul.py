import pygame
import time
import numpy as np
import math

pygame.init()


"""setting up the color scheme for the game """

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)


"""setting up the screen size"""

desktopWidth, desktopHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
pole_x_1 = 50
pole_x_2 = 800
pole_start = 50
pole_height = 500
ball_radius = 15

theta_rod = 0
gravity_accln = 0.8

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

def get_circle_coordinates(x_1, y_1, x_2, y_2, x_ball, y_ball, speed_ball):

    gravity_accln = 75

    # print x_1, y_1, x_2, y_2

    slope = float(y_1 - y_2) / (x_2 - x_1)
    theta = math.atan(slope)

    displacement_x = speed_ball + 0.5 * gravity_accln * np.sin(theta)
    print displacement_x, speed_ball, theta

    x_ball = x_ball - displacement_x * np.cos(theta)
    y_ball = -1 * slope * (x_ball - x_1) + y_1 - ball_radius

    if x_ball <= pole_x_1:
        x_ball = pole_x_1 + 2 * ball_radius

    elif x_ball >= pole_x_2:
        x_ball = pole_x_2 - ball_radius

    return (x_ball, y_ball, speed_ball)

def game_loop():

    x_1 = pole_x_1
    x_2 = pole_x_2
    y_1 = pole_start + pole_height
    y_2 = pole_start + pole_height

    speed_ball = 0

    x_ball = (x_1 + x_2) / 2
    y_ball = pole_start + (pole_height - ball_radius)

    while True:

        gameDisplay.fill(white)
        pygame.draw.circle(gameDisplay, red, (int(x_ball), int(y_ball)), ball_radius)

        blit_rod(x_1, y_1, x_2, y_2)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
            #
            #     if event.key == pygame.K_w:
            #         y_1 -= 10
            #
            #     if event.key == pygame.K_s:
            #         y_1 += 10
            #
            #     if event.key == pygame.K_UP:
            #         y_2 -= 10
            #
            #     if event.key == pygame.K_DOWN:
            #         y_2 += 10

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            y_2 += 1
        if keys[pygame.K_UP]:
            y_2 -= 1
        if keys[pygame.K_w]:
            y_1 -= 1
        if keys[pygame.K_s]:
            y_1 += 1


        (x_ball, y_ball, speed_ball) = get_circle_coordinates(x_1, y_1, x_2, y_2, x_ball, y_ball, speed_ball)

        blit_poles()
        pygame.display.update()


game_loop()
pygame.quit()
quit()
