import pygame
# import time

import numpy as np
import math

import random

import sys

import pickle
import co_ordinates

pygame.init()


"""setting up the color scheme for the game """

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)


"""setting up the screen size"""

desktopWidth, desktopHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
pole_x_1 = 50
pole_x_2 = 700
pole_start = 50
pole_height = 500

theta_rod = 0
gravity_accln = 2
game_offset = 10

display_width = 72 * int(desktopWidth/100)
display_height = 95 * int(desktopHeight/100)

"""setting the game-name and display window"""

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Hoaul')


pole = pygame.image.load('branch.png')
branch_bottom = pygame.image.load('branch_bottom.png')
rod = pygame.image.load('rod.png')
brick = pygame.image.load('brick.png')
ball = pygame.image.load('ball.png')
ball_power = pygame.image.load('ball_power.png')
# stone = [pygame.image.load("stone_1.png"), pygame.image.load("stone_2.png")]
stone = pygame.image.load('stone.png')
stone_broken = pygame.image.load('stone_broken.png')
freeze = pygame.image.load('freeze.png')
small = pygame.image.load('small.png')
# rip = pygame.image.load('rip.png')
# rip = pygame.transform.scale(rip, (display_width, display_height))

clock = pygame.time.Clock()


def blit_poles():

    for i in xrange(pole_start, pole_start + pole_height, 10):
        gameDisplay.blit(pole, (pole_x_1, i))
        gameDisplay.blit(pole, (pole_x_2, i))

    gameDisplay.blit(branch_bottom, (pole_x_1 - 42, pole_start + pole_height))
    gameDisplay.blit(branch_bottom, (pole_x_2 - 42, pole_start + pole_height))

def show_score(y_ball, holes, score):

    """ The function used to print the score on the top-left corner of screen """

    for hole_centers in holes[1:]:
        if int(y_ball) == hole_centers[0][1]:
            score += 1

    font = pygame.font.SysFont("comicsansms", 20, True, True)
    screen_text = font.render("Score : " + str(int(score)), True, black)
    gameDisplay.blit(screen_text, [0, 0])

    return score

def show_level(level):
    """ The function used to print the level on the top-left corner of screen """

    font = pygame.font.SysFont("comicsansms", 20, True, True)
    screen_text = font.render("Level : " + str(int(level)), True, black)
    gameDisplay.blit(screen_text, [0, 20])


def blit_rod(x_1, y_1, x_2, y_2):

    slope = float(y_2 - y_1) / (x_2 - x_1)

    for i in xrange(x_1, x_2):
        y = y_1 + slope * (i - x_1)
        gameDisplay.blit(rod, (i, y))

def get_circle_coordinates(x_1, y_1, x_2, y_2, x_ball, y_ball, speed_ball, ball_radius, level):

    # print x_1, y_1, x_2, y_2

    slope = float(y_1 - y_2) / (x_2 - x_1)
    theta = math.atan(slope)

    displacement_x = speed_ball + 0.5 * (gravity_accln + 20 * level) * np.sin(theta)
    # print displacement_x, speed_ball, theta

    x_ball = x_ball - displacement_x * np.cos(theta)
    y_ball = -1 * slope * (x_ball - x_1) + y_1 - ball_radius

    if x_ball < pole_x_1 + 2 * ball_radius:
        x_ball = pole_x_1 + 2 * ball_radius

    elif x_ball > pole_x_2 - ball_radius:
        x_ball = pole_x_2 - ball_radius

    return (x_ball, y_ball, speed_ball)

def check_overlap(center, holes, game_offset, brick_boolean=False, small_boolean=False):

    if small_boolean:
        game_offset /= 2
    if brick_boolean:
        game_offset *= 2
    for circle_center in holes:
        if abs(center[0] - circle_center[0][0]) < game_offset and abs(center[1] - circle_center[0][1]) < game_offset:
            if not brick_boolean:
                return True
            else:
                holes[holes.index(circle_center)][1] = "brick"
    return False

def message_to_screen(msg, color, vert_displacement=0, size=25, text_font="None", bold="False", italic="False") :

    """ Function to print a message (msg) on the game-display """

    font = pygame.font.SysFont(text_font, size, bold, italic)
    screen_text = font.render(msg, True, color)
    text_position = screen_text.get_rect()
    text_position.center = (display_width/2, display_height/2 + vert_displacement)
    gameDisplay.blit(screen_text, text_position)


def game_loop(level, score):

    x_1 = pole_x_1
    x_2 = pole_x_2
    y_1 = pole_start + pole_height
    y_2 = pole_start + pole_height

    debug_var = 0

    speed_ball = 0
    speed_hole = 1
    speed_hole_special = 1
    special_on_screen = False
    ball_radius = 15
    brick_boolean = False
    small_boolean = False
    power_taken = False

    score_touch_decreament = 0.1 * level
    score_decreament = 0.001 * level

    x_ball = (x_1 + x_2) / 2
    y_ball = pole_start + (pole_height - ball_radius)

    hole_count = 0
    holes = []
    special_holes = ["brick", "freeze", "small"]
    power = ""
    num_holes = random.randint(10 * level, 12 * level)


    while hole_count < num_holes:
        center = [random.randint(pole_x_1 + 2 * ball_radius, pole_x_2 - 2 * ball_radius),
                  random.randint(pole_start + 2 * ball_radius, pole_start + pole_height - 2 * ball_radius)]
        if not check_overlap(center, holes, game_offset):
            if hole_count == 0:
                center[1] = 0
                holes.append([center, "power"])
            else:
                holes.append([center, ""])
            hole_count += 1

    # print holes

    game_exit = False
    game_over = False

    while not game_exit:

        try:
            with open('constants.pickle', 'r+b') as f:
                shared = pickle.load(f)
        except EOFError:
            pass
        except KeyError:
            pass

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
                        sys.exit(0)

                    if event.key == pygame.K_c:
                        game_loop(level, 0.0)

                if event.type == pygame.QUIT:
                    game_exit = True
                    game_over = False

        gameDisplay.fill(white)

        for hole_num in xrange(1, hole_count):
            holes[hole_num][0][1] += speed_hole
            if holes[hole_num][0][1] >= pole_start + pole_height:
                holes[hole_num][0][1] -= pole_height
                holes[hole_num][0][0] = random.randint(pole_x_1 + 2 * ball_radius, pole_x_2 - 2 * ball_radius)
                holes[hole_num][1] = ""

        if check_overlap((x_ball, y_ball), [holes[0]], 3 * game_offset):
            power_taken = True

        if special_on_screen == True:
            holes[0][0][1] += speed_hole_special
            if holes[0][0][1] <= display_height:
                if not power_taken and holes[0][0][1] <= pole_start + pole_height:
                    if power == "brick":
                        gameDisplay.blit(brick, (holes[0][0][0], holes[0][0][1]))
                    elif power == "freeze":
                        gameDisplay.blit(freeze, (holes[0][0][0], holes[0][0][1]))
                    elif power == "small":
                        gameDisplay.blit(small, (holes[0][0][0], holes[0][0][1]))
                        # ball_radius = 8
                        # gameDisplay.blit(small, (int(x_ball) - ball_radius, int(y_ball) - ball_radius))
                elif holes[0][0][1] <= pole_start + pole_height:
                    if power == "brick":
                        brick_boolean = True
                    elif power == "freeze":
                        speed_hole = 0
                    elif power == "small":
                        small_boolean = True

            else:
                special_on_screen = False
                ball_radius = 15
                speed_hole = 1
                power_taken = False
                small_boolean = False
                brick_boolean = False
                power = ""
                holes[0][0][1] = 0
                holes[hole_num][0][0] = random.randint(pole_x_1 + 2 * ball_radius, pole_x_2 - 2 * ball_radius)

        for center in holes[1:]:
            # pygame.draw.circle(gameDisplay, black, center, ball_radius)
            if center[1] != "brick":
                gameDisplay.blit(stone, (center[0][0] - ball_radius, center[0][1] - ball_radius))
            else:
                gameDisplay.blit(stone_broken, (center[0][0] - ball_radius, center[0][1] - ball_radius))


        blit_rod(shared["x_1"], shared["y_1"], shared["x_2"], shared["y_2"])

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

        # pygame.draw.circle(gameDisplay, red, (int(x_ball), int(y_ball)), ball_radius)
        if power_taken:
            if small_boolean:
                ball_radius = 8
                gameDisplay.blit(small, (int(x_ball) - ball_radius, int(y_ball) - ball_radius))
            else:
                gameDisplay.blit(ball_power, (int(x_ball) - ball_radius, int(y_ball) - ball_radius))
        else:
            gameDisplay.blit(ball, (int(x_ball) - ball_radius, int(y_ball) - ball_radius))

        keys = pygame.key.get_pressed()

        # if keys[pygame.K_DOWN]:
        #     co_ordinates.y_2 += 1
        # if keys[pygame.K_UP]:
        #     co_ordinates.y_2 -= 1
        # if keys[pygame.K_w]:
        #     co_ordinates.y_1 -= 1
        # if keys[pygame.K_s]:
        #     co_ordinates.y_1 += 1

        y_1 = max(y_1, pole_start)
        y_1 = min(y_1, pole_start + pole_height)
        y_2 = max(y_2, pole_start)
        y_2 = min(y_2, pole_start + pole_height)

        if y_ball <= pole_start - ball_radius:
            message_to_screen("Level Up", color=red, vert_displacement=-20, size=50, text_font="helvetica",
                              bold="True")
            message_to_screen("Press C to move to next level and Q to quit", color=black, vert_displacement=35, size=25,
                              text_font="timesnewroman", italic="True")

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_exit = True
                        game_over = False
                        sys.exit(0)

                    if event.key == pygame.K_c:
                        game_loop(level + 1, score)

                if event.type == pygame.QUIT:
                    game_exit = True
                    game_over = False

        (x_ball, y_ball, speed_ball) = get_circle_coordinates(shared["x_1"], shared["y_1"], shared["x_2"],shared["y_2"], x_ball, y_ball, speed_ball, ball_radius, level)

        if check_overlap((x_ball, y_ball), holes[1:], game_offset, brick_boolean, small_boolean):
            game_over = True

        # if score == int(score):
        #     print "Ball and hole at Same level", debug_var
        #     debug_var += 1

        score = show_score(y_ball, holes, score)

        if x_ball - 2 * ball_radius == pole_x_1 or x_ball + ball_radius == pole_x_2 and y_ball > pole_start - ball_radius:
            score -= score_touch_decreament

        elif y_ball > pole_start - ball_radius:
            score -= score_decreament

        # print score

        show_level(level)

        # print score

        if score != 0 and (score % 5) == 0 and not special_on_screen:
            power = special_holes[random.randint(0, len(special_holes) - 1)]
            holes[0][1] = power
            special_on_screen = True

        blit_poles()
        pygame.display.update()

        print shared["x_1"], shared["x_2"], shared["y_1"], shared["y_2"]

if __name__ == "__main__":
    init_level = 1
    score = 0.0
    game_loop(init_level, score)
    pygame.quit()
    quit()