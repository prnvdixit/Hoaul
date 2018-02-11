from collections import deque
import cv2
import argparse
import numpy as np
import pygame
import imutils

import sys
import os

import pyautogui

import gtk
import wnck
import time

# Setting window to start from the leftmost corner of screen
os.environ['SDL_VIDEO_WINDOW_POS'] = '{0},{1}'.format(0, 0)

# Pass arguments - buffer size would mean sensitivity
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=4, help="max buffer size")
args = vars(ap.parse_args())

# Size of selection-square
crop_img_offset = 20

def select_object(frame, crop_img_offset):

    # Get mouse coordinates for object selection
    pos = pygame.mouse.get_pos()
    x_co = pos[0]
    y_co = pos[1]

    # Crop the image corresponding to the area selected
    img = frame
    img_crop = img[y_co - crop_img_offset:y_co + crop_img_offset,
               x_co - crop_img_offset:x_co + crop_img_offset]
    img = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)

    length = len(img)
    width = len(img[0])

    # Assign init values to HSV-ranges
    (max_h, min_h, max_s, min_s, max_v, min_v) = (0, 180, 0, 255, 0, 255)


    # Iterate through all the pixels and determine the HSV-range
    for i in xrange(0, length):
        for j in xrange(0, width):
            (h, s, v) = (img[i][j][0], img[i][j][1], img[i][j][2])
            max_h = max(max_h, h)
            min_h = min(min_h, h)
            max_s = max(max_s, s)
            min_s = min(min_s, s)
            max_v = max(max_v, v)
            min_v = min(min_v, v)

    # Revert back the cropped part to BGR
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

    return [(min_h, min_s, min_v), (max_h, max_s, max_v)]

def show_game_window():

    # Useful to ensure that the game-screen is always in focus
    # when simulating the key-press using pyautogui
    screen = wnck.screen_get_default()
    while gtk.events_pending():
        gtk.main_iteration()

    windows = screen.get_windows()
    for w in windows:
        if w.get_name() == 'Hoaul':
            w.activate(int(time.time()))

def detect_gesture(result, frame, pts, vector, key_up, key_down, game_display):

    # colour_lower and colour_lower are HSV-ranges for corresponding object.
    colour_lower = np.array([result[0][0], result[0][1], result[0][2]], dtype="uint8")
    colour_upper = np.array([result[1][0], result[1][1], result[1][2]], dtype="uint8")

    # Apply blurring function to reduce noise
    frame = imutils.resize(frame, width=640)
    blur_frame = cv2.GaussianBlur(frame, (15, 15), 0)
    hsv = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2HSV)

    # print colour_lower, colour_upper
    mask = cv2.inRange(hsv, colour_lower, colour_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # cv2.imshow("Mask", mask)

    # Find the contours corresponding to the colour-range
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    center = None

    # If there is atleast some contour - process the contour list
    if len(contours) > 0:

        # Find the maximum-area contour
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        center = (x + w / 2, y + h / 2)
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        pts.appendleft(center)

        # Draw a rectangle around max area contour
        pygame.draw.rect(game_display, (0, 255, 0), (x, y, w, h), 2)
        pygame.draw.rect(game_display, (0, 0, 0), (center[0], center[1], 10, 10))

        # Update the vector corresponding to the motion
        if len(pts) > 1:
            center = np.array(center)
            center = center.reshape((2, 1))
            last_element = np.array(pts[1]).reshape((2, 1))
            vector += (center - last_element)
            # print vector

    # Draw a trail to the motion
    for i in xrange(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue

        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 1.5)
        # cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)
        pygame.draw.line(game_display, (0, 255, 0), pts[i - 1], pts[i], thickness)

    # If magnitude of vector is more than the threshold
    # find the direction and blit it on the game-display
    if np.linalg.norm(vector) > 20:
        # print "Direction", vector
        # print np.linalg.norm(vector)
        d_y = vector[1]

        (_, dir_y) = ("", "")

        if np.abs(d_y) > 15:
            dir_y = "South" if np.sign(d_y) == 1 else "North"

        direction = dir_y

        vector = np.zeros((2, 1), dtype=np.int)
        pts.clear()

        if direction == "North":
            pyautogui.press(key_up)
        elif direction == "South":
            pyautogui.press(key_down)

    return (pts, vector, result)

def track():

    # Initialise the vectors for both right and
    # left colours
    right_vector = np.zeros((2, 1), dtype=np.int)
    left_vector = np.zeros((2, 1), dtype=np.int)

    # Create a capture object
    camera = cv2.VideoCapture(0)

    # fourcc = cv2.cv.CV_FOURCC(*'MJPG')
    # video = cv2.VideoWriter('output.avi', fourcc, 30.0, (640, 480))

    (grabbed, frame) = camera.read()

    # Transpose the grabbed frame to match the
    # dimensions of the pygame window
    frame = np.transpose(frame, (1, 0, 2))

    pygame.init()
    game_display = pygame.display.set_mode(frame.shape[:2])

    pygame.display.set_caption('gesture_detection')
    pygame.mouse.set_visible(False)

    # Object-attributes is initialised
    right_object_set_detect = 0
    left_object_set_detect = 0

    right_direction = ""
    left_direction = ""

    left_result = []
    right_result = []

    left_pts = deque(maxlen=args["buffer"])
    right_pts = deque(maxlen=args["buffer"])

    while True:
        (grabbed, frame) = camera.read()

        frame = cv2.flip(frame, 1)

        for event in pygame.event.get():

            # Left click on the object for left-side pole
            # Right click on the object for right-side pole
            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    right_result = select_object(frame, crop_img_offset)
                    right_object_set_detect = 1

                if event.button == 3:

                    left_result = select_object(frame, crop_img_offset)
                    left_object_set_detect = 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit(0)

                # Click 's' to stop detection
                elif event.key == pygame.K_s:
                    direction = ""

        # Convert to RGB (OpenCV compatible) from BGR (Pygame compatible)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Transpose to fit in the window
        frame = np.transpose(frame, (1, 0, 2))

        # Blit on the game-display
        pygame.surfarray.blit_array(game_display, frame)

        # Re-transpose & convert to make it openCV compatible
        frame = np.transpose(frame, (1, 0, 2))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


        # Show the rectangular selection box - To select the object
        position_mouse = pygame.mouse.get_pos()
        pygame.draw.rect(game_display, (0, 0, 0), (
        position_mouse[0] - crop_img_offset, position_mouse[1] - crop_img_offset, 2 * crop_img_offset,
        2 * crop_img_offset), 2)


        # If objects are set to detect - Detect them in frame
        if right_object_set_detect:
            (right_pts, right_vector, right_result) = detect_gesture(right_result, frame, right_pts, right_vector, 'up',
                                                                     'down', game_display)

        if left_object_set_detect:
            (left_pts, left_vector, left_result) = detect_gesture(left_result, frame, left_pts, left_vector, 'w',
                                                                     's', game_display)

        # Blit the directions on frame
        font = pygame.font.SysFont("timesnewroman", size=25, bold="False", italic="True")

        screen_text = font.render(left_direction, True, (0, 0, 255))
        text_position = screen_text.get_rect()
        text_position.center = (350, 450)
        game_display.blit(screen_text, text_position)

        screen_text = font.render(right_direction, True, (0, 0, 255))
        text_position = screen_text.get_rect()
        text_position.center = (350, 350)
        game_display.blit(screen_text, text_position)

        pygame.display.update()

        # Ensure that Pygame window is in focus when simulating the click
        show_game_window()

        # video.write(frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # print colour_upper, colour_lower
            break

track()
