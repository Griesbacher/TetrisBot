import inspect

import cv2
import numpy as np

from game_objects import blocks


def show_image(img):
    cv2.imshow("Test", cv2.resize(img, (0, 0), fx=2, fy=2))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def mem_test():
    a1 = blocks.JNoseLeft()
    a2 = blocks.JNoseRight()
    u = blocks.U()
    print a1, a2
    print a1.same_type(a2)
    print a1.same_type(u)


if __name__ == '__main__':
    mem_test()
