import operator

import copy

import numpy as np

from blocks import Block
from control import Moveset
from game_objects import blocks


class FieldException(Exception):
    pass


class OutOfBoard(FieldException):
    pass


class TooFarLeft(OutOfBoard):
    pass


class TooFarRight(OutOfBoard):
    pass


class TooHigh(OutOfBoard):
    pass


class MissingDrop(FieldException):
    pass


class GameLost(FieldException):
    pass


class Field:
    def __init__(self, width=10, height=18, new_block_index=5, board=None):
        self._width = width
        self._height = height
        if board is None:
            self._field = np.full((self._width, self._height), False, dtype=bool)
        else:
            self._field = board
        self._new_block_x = new_block_index

    def __str__(self):
        to_print = "-" * (self._width * 2 + 1) + "\n"
        for row in zip(*self._field):
            to_print += "|"
            for field in row:
                if field:
                    to_print += "x|"
                else:
                    to_print += " |"

            to_print += "\n"

        return to_print

    def get_field(self):
        return copy.deepcopy(self._field)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def copy(self):
        return Field(width=self._width, height=self._height, new_block_index=self._new_block_x, board=self.get_field())

    def add_block(self, block, moves):
        # type: (Block, list) -> (Field, int, int)
        if block.is_unknown():
            return self
        offset_x = 0
        rotations = 0
        drop = Moveset.DROP in moves
        for m in moves:
            if m == Moveset.LEFT:
                offset_x -= 1
            elif m == Moveset.RIGHT:
                offset_x += 1
            elif m == Moveset.ROTATE:
                rotations += 1
        possible_rotations = list(block.rotations_clock_wise())
        rotated_block = possible_rotations[rotations % len(possible_rotations)]
        x = self._new_block_x + offset_x
        y_start = min([e[1] for e in rotated_block.get_shape()]) * -1
        max_y = y_start
        if not self._test_if_block_fits(x, y_start, rotated_block):
            raise GameLost()
        if drop:
            for i in range(y_start + 1, self._height):
                if self._test_if_block_fits(x, i, rotated_block):
                    max_y = i
                else:
                    break
        new_field = self.copy()._place_block(x, max_y, rotated_block)
        return new_field, new_field._vanish_lines(), (self._height - max_y)

    def _test_if_block_fits(self, x, y, block):
        # type: (int, int, Block) -> bool
        base_pos = (x, y)
        for i in block.get_shape():
            pos = tuple_add(base_pos, i)
            if pos[0] < 0:
                raise TooFarLeft()
            elif pos[0] >= self._width:
                raise TooFarRight()
            else:
                try:
                    if self._field[pos]:
                        return False
                except IndexError:
                    return False
        return True

    def _place_block(self, x, y, block):
        # type: (int, int, Block) -> Field
        base_pos = (x, y)
        for i in block.get_shape():
            pos = tuple_add(base_pos, i)
            if pos[0] < 0:
                raise TooFarLeft
            elif pos[0] >= self._width:
                raise TooFarRight
            self._field[pos] = True
        return self

    def _vanish_lines(self):
        vanished = []
        zipped_field = zip(*self._field)
        for i in range(len(zipped_field)):
            if np.all(zipped_field[i]):
                vanished.append(i)
        for column in self._field:
            for line in vanished:
                for i in range(line, 1, -1):
                    column[i] = column[i - 1]
        return len(vanished)

    def block_height(self):
        # type: (None) -> int
        zipped_field = zip(*self._field)
        for i in range(len(zipped_field)):
            if np.any(zipped_field[i]):
                return self._height - i
        return 0

    def get_hole_per_line(self):
        # type: (None) -> list()
        holes = [[] for i in range(self._height)]
        for c in range(len(self._field)):
            if np.any(self._field[c]):
                current_block = -1
                for r in range(len(self._field[c])):
                    if self._field[c][r]:
                        current_block = r
                    elif current_block > 0:
                        holes[self._height - r].append(1)
        return [sum(h) for h in holes]

    def number_of_holes(self):
        # type: (None) -> int
        return sum(self.get_hole_per_line())

    def calc_hole_score(self):
        # type: (None) -> int
        """Higher holes give a higher rating"""
        holes = self.get_hole_per_line()
        return sum([i * holes[i] for i in range(len(holes))])

    def calc_hole_score_inverse(self):
        # type: (None) -> int
        """Lower holes give a higher rating"""
        holes = self.get_hole_per_line()
        return sum([len(holes) - i * holes[i] for i in range(len(holes))])

    def get_blockades(self):
        # type: (None) -> int
        blockades_per_column = []
        for c in self._field:
            first_hole = None
            last_block = None
            r_c = list(reversed(c))
            for i in range(len(r_c)):
                if not r_c[i] and first_hole is None:
                    first_hole = i
                elif r_c[i] and first_hole is not None:
                    last_block = i
                    # blockades_per_column.append(i - first_hole) method 2
            if first_hole is not None and last_block is not None:
                blockades_per_column.append(last_block - first_hole)  # method 1
        # print blockades_per_column
        return sum(blockades_per_column)

    def _test_moveset(self, block, moveset):
        try:
            self.add_block(block, moveset)
            return True
        except OutOfBoard:
            return False

    def get_possible_movesets(self, block):
        possible_movesets = []
        moveset = []
        rotations = list(block.rotations_clock_wise())
        for r in range(len(rotations)):
            if not self._test_moveset(block, moveset):
                continue
            possible_movesets.append(list(moveset + [Moveset.DROP]))
            moveset_left = list(moveset)
            for lefts in range(int(self.get_width() / 2)):
                moveset_left.append(Moveset.LEFT)
                if not self._test_moveset(block, moveset_left):
                    break
                possible_movesets.append(list(moveset_left + [Moveset.DROP]))
            moveset_right = list(moveset)
            for rights in range(int(self.get_width() / 2)):
                moveset_right.append(Moveset.RIGHT)
                if not self._test_moveset(block, moveset_right):
                    break
                possible_movesets.append(list(moveset_right + [Moveset.DROP]))
            moveset.append(Moveset.ROTATE)
        return possible_movesets


NBlox = Field(width=10, height=18, new_block_index=4)
Quadrapssel = Field(width=14, height=15, new_block_index=6)


def tuple_add(a, b):
    return tuple(map(operator.add, a, b))


if __name__ == '__main__':
    """
    f1, i, h = Field().add_block(blocks.TNoseDown(), [Moveset.DROP])
    f2, i, h = f1.add_block(blocks.TNoseDown(), [Moveset.LEFT, Moveset.LEFT, Moveset.LEFT, Moveset.DROP])
    f3, i, h = f2.add_block(blocks.TNoseDown(), [Moveset.RIGHT, Moveset.RIGHT, Moveset.RIGHT, Moveset.DROP])
    f4, i, h = f3.add_block(blocks.TNoseLeft(),
                         [Moveset.RIGHT, Moveset.RIGHT,  Moveset.RIGHT, Moveset.RIGHT, Moveset.DROP])
    f5, i, h = f4.add_block(blocks.IHorizontal(),
                         [Moveset.LEFT, Moveset.LEFT, Moveset.LEFT, Moveset.DROP])
    f6, i, h = f5.add_block(blocks.IHorizontal(), [Moveset.RIGHT, Moveset.RIGHT, Moveset.DROP])
    f7, i, h = f6.add_block(blocks.TNoseDown(), [Moveset.DROP])
    print f7, i
    t, i, h = f3.add_block(blocks.TNoseLeft(), [Moveset.DROP])
    print t
    print t.get_hole_per_line()
    print t.calc_hole_score()
    print t.calc_hole_score_inverse()

    f = Field().add_block(blocks.TNoseDown(), [Moveset.DROP])[0].add_block(blocks.TNoseLeft(), [Moveset.DROP])[0]
    print f
    f.get_blockades()
    """
    print Field().get_possible_movesets(blocks.IHorizontal())
