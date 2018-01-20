import copy_reg
import time
import types

import multiprocessing

from game_objects.blocks import Block
from game_objects.field import FieldException
from recorder import Recorder
from shared_obj import shared_objects


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)


copy_reg.pickle(types.MethodType, _pickle_method)


class KeepLowTwice:
    def __init__(self, field, controller=None,
                 factors=[1.85639262e-04, 6.35249496e-04, -8.22603703e-06, -4.68157053e-04], multi_processing=False):
        self._field = field
        self._controller = controller
        self._scores = {}
        self._blocks_moved = 0
        self._f = factors
        self._multi_processing = multi_processing
        if self._multi_processing:
            if shared_objects["process_pool"] is None:
                raise Exception("process_pool has not been init")

    def calc_move_and_move(self, c_block, n_block):
        if self._controller is not None:
            moveset = self.calc_move(c_block, n_block)
            self._controller.move_block(moveset)
        else:
            print "no controller has been given, doing nothing..."

    def calc_move(self, c_block, n_block):
        # type: (Block, Block) -> list()
        self._blocks_moved += 1
        c_movesets = self._field.get_possible_movesets(c_block)
        n_movesets = []
        if n_block is not None:
            n_movesets = self._field.get_possible_movesets(n_block)
        self._scores = {}
        if not self._multi_processing:
            for c_m in c_movesets:
                self._scores.update(self._test_combinations(c_block, n_block, c_m, n_movesets))
        else:
            for r in shared_objects["process_pool"].map(self._capsulate_test_combinations,
                                                        [(c_block, n_block, c_m, n_movesets) for c_m in c_movesets]):
                self._scores.update(r)
        lowest_score = min(self._scores.keys())
        moveset = self._scores[lowest_score]
        self._field, _, _ = self._field.add_block(c_block, moveset)
        self._scores = {}
        return moveset

    def _capsulate_test_combinations(self, args):
        if len(args) == 4:
            return self._test_combinations(args[0], args[1], args[2], args[3])

    def _test_combinations(self, c_block, n_block, move, n_movesets):
        scores = {}
        try:
            c_field, c_score = self._calc_score(self._field, c_block, move)
            if n_block is None:
                scores[c_score] = move
            else:
                for n_m in n_movesets:
                    try:
                        n_field, n_score = self._calc_score(c_field, n_block, n_m)
                        scores[c_score + n_score] = move
                    except FieldException:
                        pass
        except FieldException:
            pass
        return scores

    def _calc_score(self, field, block, moveset):
        new_field, vanished_lines, height = field.add_block(block, moveset)
        score = self._f[0] * new_field.calc_hole_score() + \
                self._f[1] * height + \
                self._f[2] * new_field.get_blockades() + \
                self._f[3] * vanished_lines
        return new_field, score


if __name__ == '__main__':
    from game_objects.field import NBlox

    shared_objects["process_pool"] = multiprocessing.Pool()
    ai = KeepLowTwice(NBlox, multi_processing=True)
    i = 0
    start = time.time()
    for c, n in Recorder(NBlox.get_width()).play_all_at_once(NBlox.get_width()):
        try:
            ai.calc_move(c, n)
        except Exception as e:
            print "Failed at %d " % i
            print e
            break
        if i == 100:
            break
        i += 1
    print "took: %ds" % (time.time() - start)
    # 10 - 11s single
