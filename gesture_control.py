from collections import deque
import cv2
import argparse
import numpy as np
import pygame
import imutils

import sys

import os
from collections import Counter

os.environ['SDL_VIDEO_WINDOW_POS'] = '{0},{1}'.format(0, 0)

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=4, help="max buffer size")
args = vars(ap.parse_args())

crop_img_offset = 20

left_pts = deque(maxlen=args["buffer"])
right_pts = deque(maxlen=args["buffer"])

def track():

    right_vector = np.zeros((2, 1), dtype=np.int)
    left_vector = np.zeros((2, 1), dtype=np.int)

    camera = cv2.VideoCapture(0)

    # fourcc = cv2.cv.CV_FOURCC(*'MJPG')
    # video = cv2.VideoWriter('output.avi', fourcc, 30.0, (640, 480))

    (grabbed, frame) = camera.read()

    frame = np.transpose(frame, (1, 0, 2))

    pygame.init()
    game_display = pygame.display.set_mode(frame.shape[:2])

    pygame.display.set_caption('gesture_detection')
    pygame.mouse.set_visible(False)

    right_object_set_detect = 0
    left_object_set_detect = 0

    right_direction = ""
    left_direction = ""

    left_result = []
    right_result = []

    while True:
        (grabbed, frame) = camera.read()

        frame = cv2.flip(frame, 1)

        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    x_co = pos[0]
                    y_co = pos[1]

                    img = frame

                    img_crop = img[y_co - crop_img_offset:y_co + crop_img_offset,
                               x_co - crop_img_offset:x_co + crop_img_offset]
                    img = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)

                    length = len(img)
                    width = len(img[0])

                    (max_h, min_h, max_s, min_s, max_v, min_v) = (0, 180, 0, 255, 0, 255)

                    for i in xrange(0, length):
                        for j in xrange(0, width):
                            (h, s, v) = (img[i][j][0], img[i][j][1], img[i][j][2])
                            max_h = max(max_h, h)
                            min_h = min(min_h, h)
                            max_s = max(max_s, s)
                            min_s = min(min_s, s)
                            max_v = max(max_v, v)
                            min_v = min(min_v, v)

                    right_result = [(min_h, min_s, min_v), (max_h, max_s, max_v)]

                    right_object_set_detect = 1

                    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

                # if event.button == 3:
                #     pos = pygame.mouse.get_pos()
                #     x_co = pos[0]
                #     y_co = pos[1]
                #
                #     img = frame
                #
                #     img_crop = img[y_co - crop_img_offset:y_co + crop_img_offset,
                #                x_co - crop_img_offset:x_co + crop_img_offset]
                #     img = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)
                #
                #     length = len(img)
                #     width = len(img[0])
                #
                #     (max_h, min_h, max_s, min_s, max_v, min_v) = (0, 180, 0, 255, 0, 255)
                #
                #     for i in xrange(0, length):
                #         for j in xrange(0, width):
                #             (h, s, v) = (img[i][j][0], img[i][j][1], img[i][j][2])
                #             max_h = max(max_h, h)
                #             min_h = min(min_h, h)
                #             max_s = max(max_s, s)
                #             min_s = min(min_s, s)
                #             max_v = max(max_v, v)
                #             min_v = min(min_v, v)
                #
                #     left_result = [(min_h, min_s, min_v), (max_h, max_s, max_v)]
                #
                #     left_object_set_detect = 1
                #
                #     img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit(0)

                elif event.key == pygame.K_s:
                    pts.clear()
                    object_set_to_be_detected = 1 - object_set_to_be_detected
                    direction = ""
                    constants.mode = ""

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.transpose(frame, (1, 0, 2))
        pygame.surfarray.blit_array(game_display, frame)
        frame = np.transpose(frame, (1, 0, 2))

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        position_mouse = pygame.mouse.get_pos()
        pygame.draw.rect(game_display, (0, 0, 0), (
        position_mouse[0] - crop_img_offset, position_mouse[1] - crop_img_offset, 2 * crop_img_offset,
        2 * crop_img_offset), 2)


        if right_object_set_detect:
            colour_lower = np.array([right_result[0][0], right_result[0][1], right_result[0][2]], dtype="uint8")
            colour_upper = np.array([right_result[1][0], right_result[1][1], right_result[1][2]], dtype="uint8")

            frame = imutils.resize(frame, width=640)
            blur_frame = cv2.GaussianBlur(frame, (15, 15), 0)
            hsv = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2HSV)

            # print colour_lower, colour_upper
            mask = cv2.inRange(hsv, colour_lower, colour_upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            cv2.imshow("Mask", mask)

            contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            center = None

            if len(contours) > 0:
                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)

                center = (x + w / 2, y + h / 2)
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                right_pts.appendleft(center)

                pygame.draw.rect(game_display, (0, 255, 0), (x, y, w, h), 2)
                pygame.draw.rect(game_display, (0, 0, 0), (center[0], center[1], 10, 10))

                if len(right_pts) > 1:
                    center = np.array(center)
                    center = center.reshape((2, 1))
                    last_element = np.array(right_pts[1]).reshape((2, 1))
                    right_vector += (center - last_element)
                    # print vector

            for i in xrange(1, len(right_pts)):
                if right_pts[i - 1] is None or right_pts[i] is None:
                    continue

                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 1.5)
                # cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)
                pygame.draw.line(game_display, (0, 255, 0), right_pts[i - 1], right_pts[i], thickness)

            if np.linalg.norm(right_vector) > 20:
                # print "Direction", vector
                # print np.linalg.norm(vector)
                d_y = right_vector[1]

                (dir_x, dir_y) = ("", "")

                if np.abs(d_y) > 15:
                    dir_y = "South" if np.sign(d_y) == 1 else "North"

                if dir_x == "":
                    right_direction = dir_y
                elif dir_y == "":
                    right_direction = dir_x
                else:
                    right_direction = dir_x if abs(d_y) / abs(d_x) >= 1 else dir_y

                right_vector = np.zeros((2, 1), dtype=np.int)
                print "Right", right_direction

        # if left_object_set_detect:
        #     colour_lower = np.array([left_result[0][0], left_result[0][1], left_result[0][2]], dtype="uint8")
        #     colour_upper = np.array([left_result[1][0], left_result[1][1], left_result[1][2]], dtype="uint8")
        #
        #     frame = imutils.resize(frame, width=640)
        #     blur_frame = cv2.GaussianBlur(frame, (15, 15), 0)
        #     hsv = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2HSV)
        #
        #     # print colour_lower, colour_upper
        #     mask = cv2.inRange(hsv, colour_lower, colour_upper)
        #     mask = cv2.erode(mask, None, iterations=2)
        #     mask = cv2.dilate(mask, None, iterations=2)
        #
        #     cv2.imshow("Mask_II", mask)
        #
        #     contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        #
        #     center = None
        #
        #     if len(contours) > 0:
        #         c = max(contours, key=cv2.contourArea)
        #         x, y, w, h = cv2.boundingRect(c)
        #
        #         center = (x + w / 2, y + h / 2)
        #         # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #         left_pts.appendleft(center)
        #
        #         pygame.draw.rect(game_display, (0, 255, 0), (x, y, w, h), 2)
        #         pygame.draw.rect(game_display, (0, 0, 0), (center[0], center[1], 10, 10))
        #
        #         if len(left_pts) > 1:
        #             center = np.array(center)
        #             center = center.reshape((2, 1))
        #             last_element = np.array(left_pts[1]).reshape((2, 1))
        #             left_vector += (center - last_element)
        #             # print vector
        #
        #     for i in xrange(1, len(left_pts)):
        #         if left_pts[i - 1] is None or left_pts[i] is None:
        #             continue
        #
        #         thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 1.5)
        #         # cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)
        #         pygame.draw.line(game_display, (0, 255, 0), left_pts[i - 1], left_pts[i], thickness)
        #
        #     if np.linalg.norm(left_vector) > 20:
        #         # print "Direction", vector
        #         # print np.linalg.norm(vector)
        #         d_y = left_vector[1]
        #
        #         (dir_x, dir_y) = ("", "")
        #
        #         if np.abs(d_y) > 15:
        #             dir_y = "South" if np.sign(d_y) == 1 else "North"
        #
        #         if dir_x == "":
        #             left_direction = dir_y
        #         elif dir_y == "":
        #             left_direction = dir_x
        #         else:
        #             left_direction = dir_x if abs(d_y) / abs(d_x) >= 1 else dir_y
        #
        #         left_vector = np.zeros((2, 1), dtype=np.int)
        #         print "Left", left_direction

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

        # video.write(frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # print colour_upper, colour_lower
            break

track()
