from game_objects.blocks import Block
from game_objects.control import Moveset
from game_objects.field import OutOfBoard
from recorder import Recorder


class KeepLow:
    def __init__(self, field, controller=None,
                 factors=[0.00018783, 0.00029767, 0.00013604, -0.00033268]):
        self._field = field
        self._controller = controller
        self._scores = {}
        self._blocks_moved = 0
        self._f = factors

    def calc_move_and_move(self, c_block, n_block):
        if self._controller is not None:
            moveset = self.calc_move(c_block, n_block)
            self._controller.move_block(moveset)

    def calc_move(self, c_block, n_block):
        # type: (Block, Block) -> list()
        self._blocks_moved += 1
        moveset = []
        rotations = list(c_block.rotations_clock_wise())
        for r in range(len(rotations)):
            self._calc_score(c_block, moveset)
            moveset_left = list(moveset)
            for lefts in range(int(self._field.get_width() / 2)):
                moveset_left.append(Moveset.LEFT)
                if not self._calc_score(c_block, moveset_left):
                    break
            moveset_right = list(moveset)
            for rights in range(int(self._field.get_width() / 2)):
                moveset_right.append(Moveset.RIGHT)
                if not self._calc_score(c_block, moveset_right):
                    break
            moveset.append(Moveset.ROTATE)
        return self._get_best_score()

    def _calc_score(self, block, moveset):
        final_moveset = list(moveset)
        if len(final_moveset) == 0 or final_moveset[-1] != Moveset.DROP:
            final_moveset.append(Moveset.DROP)
        try:
            field, vanished_lines, height = self._field.add_block(block, final_moveset)
            # score = (self._f[0] * field.calc_hole_score() + self._f[1] * height + self._f[2] * field.get_blockades())
            # if vanished_lines > 0 and self._f[3] != 0:
            #    score /= self._f[3] * vanished_lines
            score = self._f[0] * field.calc_hole_score() + self._f[1] * height + self._f[2] * field.get_blockades() + \
                    self._f[3] * vanished_lines
            if score not in self._scores:
                self._scores[score] = (field, final_moveset)
        except OutOfBoard:
            return False
        return True

    def _get_best_score(self):
        lowest_score = min(self._scores.keys())
        self._field = self._scores[lowest_score][0]
        moveset = self._scores[lowest_score][1]
        self._scores = {}
        return moveset


if __name__ == '__main__':
    from game_objects.field import NBlox

    ai = KeepLow(NBlox)
    i = 0
    for c, n in Recorder(NBlox.get_width()).play_all_at_once(NBlox.get_width()):
        try:
            ai.calc_move(c, n)
        except Exception:
            print "Failed at %d " % i
            break
        i += 1
