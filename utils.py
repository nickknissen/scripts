import numpy as np
import cv2
import math
from scipy import ndimage


def detect_angle(src, debug=False):
    lines = cv2.HoughLinesP(src, 1, math.pi / 180.0, 140, minLineLength=100, maxLineGap=5)

    angles = []

    for x1, y1, x2, y2 in lines[0]:
        if debug:
            debug_image = src.copy()
            cv2.line(debug_image, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    return  np.median(angles)


def rotate_image(src, angle):
    return ndimage.rotate(src, angle)
