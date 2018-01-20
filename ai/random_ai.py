import random

import time

from game_objects.control import Moveset
from game_objects.field import  OutOfBoard


class RandomAI():
    def __init__(self, board_monitor, control, field):
        # type (BoardMonitor, Controller, Field)-> None
        self._board_monitor = board_monitor
        self._control = control
        self._field = field
        self._running = False
        self._randomizer = random.SystemRandom()

    def run(self):
        print "Starting ai Loop"
        self._running = True
        c_block, n_block = self._board_monitor.pull()
        while c_block.is_unknown():
            c_block, n_block = self._board_monitor.pull()
        print "Found first not unknown"
        while self._running:
            print c_block
            moves = self.calc_move(c_block, n_block)
            self._control.move_block(moves)
            time.sleep(0.7)
            c_block, n_block = self._board_monitor.pull()

    def calc_move(self, c_block, n_block):
        lefts = self._randomizer.randint(0, int(self._field.get_width() / 2))
        rights = self._randomizer.randint(0, int(self._field.get_width() / 2))
        rotation_possibilities = list(c_block.rotations_clock_wise())
        rotation = self._randomizer.choice(rotation_possibilities)
        moves = []
        for l in range(lefts):
            moves.append(Moveset.LEFT)
        for r in range(rights):
            moves.append(Moveset.RIGHT)
        for r in range(rotation_possibilities.index(rotation)):
            moves.append(Moveset.ROTATE)

        moves.append(Moveset.DROP)
        try:
            self._field = self._field.add_block(rotation, moves)
        except OutOfBoard:
            self.calc_move(c_block, n_block)
        return moves
