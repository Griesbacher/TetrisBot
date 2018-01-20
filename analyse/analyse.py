import os
import sys

import cv2
import numpy as np
from PIL import Image

import game_objects.blocks as shapes
from debug import show_image


class Analyser:
    def __init__(self, block_size):
        self._block_size = float(block_size)
        self._filters = [
            self.default_filter,
            self.reverse_default_filter,
            self.friends_filter,
        ]

    def _update_block_size(self, block_size):
        pass
        #self._block_size = (self._block_size + float(block_size)) / 2

    def get_block_size(self):
        return self._block_size

    @staticmethod
    def friends_filter(img):
        # type: (np.ndarray) -> np.ndarray
        bin_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return bin_img

    @staticmethod
    def reverse_default_filter(img):
        # type: (np.ndarray) -> np.ndarray
        uniques = np.unique(img, return_counts=True)
        background_color = uniques[0][list(uniques[1]).index(max(uniques[1]))]
        img = np.where(img != background_color, 1, img)
        img = np.where(img == background_color, 255, img)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        return img

    @staticmethod
    def default_filter(img):
        # type: (np.ndarray) -> np.ndarray
        uniques = np.unique(img, return_counts=True)
        background_color = uniques[0][list(uniques[1]).index(max(uniques[1]))]
        img = np.where(img != background_color, 254, img)
        img = np.where(img == background_color, 1, img)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        return img

    def get_shape(self, image, crop_bottom=False, filter_list=None):
        if filter_list is None:
            filter_list = self._filters
        for f in filter_list:
            result = self.get_shape_with_filter(image, f, crop_bottom)
            if result is not None and not isinstance(result, shapes.U):
                return result
        return shapes.U("Could not find a suitable filter :(")

    def get_shape_with_filter(self, image, img_filter, crop_bottom=False):
        # type: (Image.Image) -> shapes.Block
        gray_img = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2GRAY)
        bin_img = img_filter(gray_img)
        #show_image(gray_img)
        #show_image(bin_img)
        features = cv2.goodFeaturesToTrack(bin_img, 15, 0.05, int(self._block_size * 0.5))
        if features is None:
            return shapes.U("Could not detect any feature")
        corners = [list(c[0]) for c in features]
        corners = self._filter_out_img_corners(corners, bin_img.shape, self._block_size / 2)
        if bin_img.shape[0] > 5 * self._block_size and bin_img.shape[1] > 5 * self._block_size:
            corners = self._filter_out_img_borders(corners, bin_img.shape, self._block_size)
        if crop_bottom:
            corners = self._filter_out_img_bottom(corners, bin_img.shape, self._block_size * 2)
        level_x = group_by_level(corners, same_x_level, self._block_size * 0.1)
        level_y = group_by_level(corners, same_y_level, self._block_size * 0.1)

        if len(corners) == 4 and len(level_x) == 2 and len(level_y) == 2:
            return self._detect_i_or_o(level_x, level_y)
        elif len(corners) == 6 and len(level_x) == 3 and len(level_y) == 3:
            return self._detect_l_or_j(level_x, level_y)
        elif len(corners) == 8:
            t = self._detect_t(level_x, level_y)
            if t is not None:
                return t
            return self._detect_s_or_z(level_x, level_y)
        else:
            return shapes.U("Could not detect shape. Corners: %s" % corners)

    def _detect_i_or_o(self, level_x, level_y):
        delta_x_1 = abs(level_y[0][0][0] - level_y[0][1][0])
        delta_x_2 = abs(level_y[1][0][0] - level_y[1][1][0])
        delta_y_1 = abs(level_x[0][0][1] - level_x[0][1][1])
        delta_y_2 = abs(level_x[1][0][1] - level_x[1][1][1])
        if not roughly_same(delta_x_1, delta_x_2, self._block_size / 4) or \
                not roughly_same(delta_y_1, delta_y_2, self._block_size / 4):
            return shapes.U("I/O Blocks are oddly shaped")
        if roughly_same(delta_x_1, delta_y_1, self._block_size / 4):
            return shapes.O()
        else:
            self._update_block_size(max(delta_x_1, delta_y_1) / 3)
            if delta_x_1 > delta_y_1:
                return shapes.IHorizontal()
            else:
                return shapes.IHorizontal()

    def _detect_l_or_j(self, level_x, level_y):
        try:
            distances_x = [abs(pair[0][1] - pair[1][1]) for pair in level_x]
            distances_y = [abs(pair[0][0] - pair[1][0]) for pair in level_y]
        except Exception:
            print level_x
            print level_y
            return None
        max_delta_x = max(distances_y)
        max_delta_y = max(distances_x)
        max_pair_x = level_x[distances_x.index(max_delta_y)]
        max_pair_y = level_y[distances_y.index(max_delta_x)]
        if not roughly_same(abs(max_delta_y - max_delta_x), self._block_size, self._block_size / 2):
            return shapes.U("L/J Blocks are oddly shaped.")
        self._update_block_size(max(max_delta_x, max_delta_y) / 3)
        min_x = min(max_pair_y[0][0], max_pair_y[1][0])
        max_x = max(max_pair_y[0][0], max_pair_y[1][0])
        min_y = min(max_pair_x[0][1], max_pair_x[1][1])
        max_y = max(max_pair_x[0][1], max_pair_x[1][1])

        if max_delta_x < max_delta_y:
            # standing
            if roughly_same(min_x, max_pair_x[0][0], self._block_size / 2):
                # nose right
                nose = max_pair_y[0] if max_pair_y[0][0] == max_x else max_pair_y[1]
                if roughly_same(min_y, nose[1], self._block_size / 2):
                    return shapes.JNoseRight()
                else:
                    return shapes.LNoseRight()
            else:
                # nose left
                nose = max_pair_y[0] if max_pair_y[0][0] == min_x else max_pair_y[1]
                if roughly_same(max_y, nose[1], self._block_size / 2):
                    return shapes.JNoseLeft()
                else:
                    return shapes.LNoseLeft()
        else:
            # laying
            if roughly_same(max_y, max_pair_y[0][1], self._block_size / 2):
                # nose up
                nose = max_pair_x[0] if max_pair_x[0][1] == min_y else max_pair_x[1]
                if roughly_same(min_x, nose[0], self._block_size / 2):
                    return shapes.JNoseUp()
                else:
                    return shapes.LNoseUp()
            else:
                # nose down
                nose = max_pair_x[0] if max_pair_x[0][1] == max_y else max_pair_x[1]
                if roughly_same(max_x, nose[0], self._block_size / 2):
                    return shapes.JNoseDown()
                else:
                    return shapes.LNoseDown()

    def _detect_t(self, level_x, level_y):
        distances_x = [abs(pair[0][1] - pair[1][1]) if len(pair) == 2 else None for pair in level_x]
        distances_y = [abs(pair[0][0] - pair[1][0]) if len(pair) == 2 else None for pair in level_y]
        if len(distances_x) == 0 or len(distances_y) == 0:
            return None
        max_delta_x = max(distances_x)
        max_delta_y = max(distances_y)
        deltas_x = [x for x in distances_x if x is not None]
        deltas_y = [x for x in distances_y if x is not None]
        if len(deltas_x) == 0 or len(deltas_y) == 0:
            return None
        min_delta_x = min(deltas_x)
        min_delta_y = min(deltas_y)
        if not roughly_same(min(max_delta_x, max_delta_y) * 3, max(max_delta_x, max_delta_y), self._block_size / 2) \
                or not roughly_same(min(min_delta_x, min_delta_y), max(min_delta_x, min_delta_y), self._block_size / 2):
            return None
        if max_delta_x > max_delta_y:
            # vertical
            nose = level_x[distances_x.index(min_delta_x)]
            base = level_x[distances_x.index(max_delta_x)]
            if nose[0][0] < base[0][0]:
                return shapes.TNoseLeft()
            else:
                return shapes.TNoseRight()
        else:
            # horizontal
            nose = level_y[distances_y.index(min_delta_y)]
            base = level_y[distances_y.index(max_delta_y)]
            if nose[0][1] < base[0][1]:
                return shapes.TNoseUp()
            else:
                return shapes.TNoseDown()

    def _detect_s_or_z(self, level_x, level_y):
        distances_x = [abs(pair[0][1] - pair[1][1]) if len(pair) == 2 else None for pair in level_x]
        distances_y = [abs(pair[0][0] - pair[1][0]) if len(pair) == 2 else None for pair in level_y]
        if len(distances_x) == 0 or len(distances_y) == 0:
            return None
        max_delta_x = max(distances_x)
        max_delta_y = max(distances_y)
        min_x = min([pair[0][0] if len(pair) == 2 else sys.maxint for pair in level_x])
        min_y = min([pair[0][1] if len(pair) == 2 else sys.maxint for pair in level_y])
        # TODO: check fail criteria
        # if not roughly_same(max_delta_x, min_delta_x, self._block_size / 2) \
        #        or not roughly_same(max_delta_y, min_delta_y, self._block_size / 2):
        #    return shapes.U("S/Z Blocks are oddly shaped.")
        if max_delta_y > max_delta_x:
            # horizontal
            for i in range(len(distances_y)):
                if distances_y[i] is not None:
                    if [min_x, min_y] in level_y[i]:
                        return shapes.ZHorizontal()
            return shapes.SHorizontal()
        else:
            # vertical
            for i in range(len(distances_y)):
                if distances_y[i] is not None:
                    if [min_x, min_y] in level_y[i]:
                        return shapes.SVertical()
            return shapes.ZVertical()

    @staticmethod
    def _filter_out_img_corners(corners, img_shape, distance):
        result = []
        x_max = img_shape[1]
        y_max = img_shape[0]
        for c in corners:
            if c[0] < distance and c[1] < distance:
                # top left
                continue
            if c[0] < distance and c[1] > y_max - distance:
                # top right
                continue
            if c[0] > x_max - distance and c[1] > y_max - distance:
                # bottom right
                continue
            if c[0] > x_max - distance and c[1] < distance:
                # bottom left
                continue
            result.append(c)
        return result

    @staticmethod
    def _filter_out_img_borders(corners, img_shape, distance):
        result = []
        x_max = img_shape[1]
        y_max = img_shape[0]
        for c in corners:
            if c[1] < distance:
                # left
                continue
            if c[1] > y_max - distance:
                #  right
                continue
            if c[0] > x_max - distance:
                # bottom
                continue
            if c[0] < distance:
                # top
                continue
            result.append(c)
        return result

    @staticmethod
    def _filter_out_img_bottom(corners, img_shape, distance):
        result = []
        x_max = img_shape[1]
        for c in corners:
            if c[0] > x_max - distance:
                # bottom
                continue
            result.append(c)
        return result


def group_by_level(points, group_func, delta):
    result = []
    for p in points:
        found = False
        for r in result:
            if group_func(p, r[0], delta):
                r.append(p)
                found = True
                break
        if not found:
            result.append([p])
    filtered_result = list()
    for r in result:
        if len(r) > 1:
            filtered_result.append(r)
    return filtered_result


def same_x_level(p1, p2, epsilon):
    return roughly_same(p1[0], p2[0], epsilon)


def same_y_level(p1, p2, epsilon):
    return roughly_same(p1[1], p2[1], epsilon)


def roughly_same(number1, number2, epsilon):
    return abs(number1 - number2) < epsilon


def test_folder(path, f=None):
    test_analyser = Analyser(30)
    print "-" * 10, path, "-" * 10
    for filename in os.listdir(path):
        if f is None:
            print filename, test_analyser.get_shape(Image.open(os.path.join(path, filename)))
        else:
            print filename, test_analyser.get_shape_with_filter(Image.open(os.path.join(path, filename)), f)
        break


if __name__ == '__main__':
    a = Analyser(30)
    # print a.get_shape(Image.open("../test/img/blocks/friends/T.png"))
    # print a.get_shape_with_filter(Image.open("../test/img/blocks/nblox/S.png"), a.default_filter)
    # print a.get_shape(Image.open("../test/img/blocks/nblox/field.png"))
    test_folder("../test/img/blocks/friends/")
    # test_folder("../test/img/blocks/nblox/")
    # test_folder("../test/img/blocks/quadrapassel/")
