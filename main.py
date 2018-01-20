import multiprocessing

import sys

from ai.keep_low import KeepLow
from ai.keep_low_twice import KeepLowTwice
from analyse.boardmonitor import BoardMonitor
from game_objects.control import Controller
from game_objects.field import NBlox, Quadrapssel
from recorder import Recorder
from shared_obj import shared_objects


def record():
    b = BoardMonitor(
        # field_region=(175, 221, 339, 607),
        # next_region=(531, 221, 254, 132),
    )
    c = Controller()
    f = NBlox
    rec = Recorder(f.get_width())
    b.register_block_callback(rec.rec_callback)
    b.push()


def play():
    # NBlox
    # b = BoardMonitor(field_region=(175, 221, 339, 607), next_region=(531, 221, 254, 132))
    b = BoardMonitor(
        field_region=(407, 267, 182, 363), next_region=(605, 293, 72, 56)
    )
    c = Controller(key_pause=1)
    f = NBlox
    # ai = KeepLow(f, c)
    shared_objects["process_pool"] = multiprocessing.Pool()
    ai = KeepLowTwice(f, controller=c, multi_processing=True)
    b.register_block_callback(ai.calc_move_and_move)
    b.push_wait()


def play_and_record():
    b = BoardMonitor(
        field_region=(175, 221, 339, 607),
        next_region=(531, 221, 254, 132),
    )
    c = Controller()
    f = NBlox
    ai = KeepLow(f, c)
    rec = Recorder(f.get_width())
    b.register_block_callback(rec.rec_callback)
    b.register_block_callback(ai.calc_move_and_move)
    b.push()


if __name__ == '__main__':
    play()
