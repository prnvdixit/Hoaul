import pygame
import time
import numpy as np
import math
import random

pygame.init()


"""setting up the color scheme for the game """

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)


"""setting up the screen size"""

desktopWidth, desktopHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
pole_x_1 = 50
pole_x_2 = 600
pole_start = 50
pole_height = 500
ball_radius = 15

theta_rod = 0
gravity_accln = 100
game_offset = 8

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

def show_score(y_ball, holes) :

    """ The function used to print the score on the top-left corner of screen """

    score = 0

    for circle_centers in holes:
        if y_ball < circle_centers[1]:
            score += 1

    font = pygame.font.SysFont("comicsansms", 20, True, True)
    screen_text = font.render("Score : " + str(score), True, black)
    gameDisplay.blit(screen_text, [0, 0])


def blit_rod(x_1, y_1, x_2, y_2):

    slope = float(y_2 - y_1) / (x_2 - x_1)

    for i in xrange(x_1, x_2):
        y = y_1 + slope * (i - x_1)
        gameDisplay.blit(rod, (i, y))

def get_circle_coordinates(x_1, y_1, x_2, y_2, x_ball, y_ball, speed_ball):

    # print x_1, y_1, x_2, y_2

    slope = float(y_1 - y_2) / (x_2 - x_1)
    theta = math.atan(slope)

    displacement_x = speed_ball + 0.5 * gravity_accln * np.sin(theta)
    # print displacement_x, speed_ball, theta

    x_ball = x_ball - displacement_x * np.cos(theta)
    y_ball = -1 * slope * (x_ball - x_1) + y_1 - ball_radius

    if x_ball < pole_x_1 + 2 * ball_radius:
        x_ball = pole_x_1 + 2 * ball_radius

    elif x_ball > pole_x_2 - ball_radius:
        x_ball = pole_x_2 - ball_radius

    return (x_ball, y_ball, speed_ball)

def check_overlap(center, holes):

    for circle_center in holes:
        if abs(center[0] - circle_center[0]) < game_offset and abs(center[1] - circle_center[1]) < game_offset:
            return True
    return False

def message_to_screen(msg, color, vert_displacement=0, size=25, text_font="None", bold="False", italic="False") :

    """ Function to print a message (msg) on the game-display """

    font = pygame.font.SysFont(text_font, size, bold, italic)
    screen_text = font.render(msg, True, color)
    text_position = screen_text.get_rect()
    text_position.center = (display_width/2, display_height/2 + vert_displacement)
    gameDisplay.blit(screen_text, text_position)



def game_loop():

    x_1 = pole_x_1
    x_2 = pole_x_2
    y_1 = pole_start + pole_height
    y_2 = pole_start + pole_height

    speed_ball = 0

    x_ball = (x_1 + x_2) / 2
    y_ball = pole_start + (pole_height - ball_radius)

    hole_count = 0
    holes = []
    num_holes = random.randint(40, 45)


    while hole_count < num_holes:
        center = (random.randint(pole_x_1 + ball_radius, pole_x_2 - ball_radius),
                  random.randint(pole_start + ball_radius, pole_start + pole_height - ball_radius))
        if not check_overlap(center, holes):
            hole_count += 1
            holes.append(center)
            pygame.display.update()

    # print holes

    game_exit = False
    game_over = False

    while not game_exit:

        while game_over:
            message_to_screen("Game Over", color=red, vert_displacement=-20, size=50, text_font="helvetica",
                              bold="True")
            message_to_screen("Press C to continue playing and Q to quit", color=black, vert_displacement=35, size=25,
                              text_font="timesnewroman", italic="True")
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_exit = True
                        game_over = False

                    if event.key == pygame.K_c:
                        gameLoop()

                if event.type == pygame.QUIT:
                    game_exit = True
                    game_over = False

        gameDisplay.fill(white)
        pygame.draw.circle(gameDisplay, red, (int(x_ball), int(y_ball)), ball_radius)

        for center in holes:
            pygame.draw.circle(gameDisplay, black, center, ball_radius)

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

        if check_overlap((x_ball, y_ball), holes):
            game_over = True

        show_score(y_ball, holes)

        blit_poles()
        pygame.display.update()


game_loop()
pygame.quit()
quit()
