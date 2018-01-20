import random


def valid_block(block):
    Block.valid_blocks.append(block)
    return block


class Block(object):
    valid_blocks = list()
    _shape = list()
    _randomizer = random.SystemRandom()

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def _next(self):
        return self

    def _previous(self):
        return self

    def same_type(self, other):
        for s in type(self).__bases__:
            if s not in type(other).__bases__:
                return False
        return True

    def rotations_clock_wise(self):
        current_rotation = self._next()
        yield self
        while not isinstance(current_rotation, self.__class__):
            yield current_rotation
            current_rotation = current_rotation._next()

    def rotations_counter_clock_wise(self):
        current_rotation = self._previous()
        yield self
        while not isinstance(current_rotation, self.__class__):
            yield current_rotation
            current_rotation = current_rotation._previous()

    def get_shape(self):
        return list(self._shape)

    @staticmethod
    def get_random_block():
        # type: (None) -> Block
        return Block._randomizer.choice(Block.valid_blocks)()

    def is_unknown(self):
        return isinstance(self, U)


@valid_block
class O(Block):
    _shape = [(0, 0), (1, 0), (1, 1), (0, 1)]
    pass


class I(Block):
    pass


@valid_block
class IVertical(I):
    _shape = [(0, 0), (0, -1), (0, 1), (0, 2)]

    def _next(self):
        return IHorizontal()

    def _previous(self):
        return IHorizontal()


@valid_block
class IHorizontal(I):
    _shape = [(0, 0), (-1, 0), (1, 0), (2, 0)]

    def _next(self):
        return IVertical()

    def _previous(self):
        return IVertical()


class J(Block):
    pass


@valid_block
class JNoseUp(J):
    _shape = [(0, 0), (1, 0), (-1, 0), (-1, -1)]

    def _next(self):
        return JNoseRight()

    def _previous(self):
        return JNoseLeft()


@valid_block
class JNoseRight(J):
    _shape = [(0, 0), (0, 1), (0, -1), (1, -1)]

    def _next(self):
        return JNoseDown()

    def _previous(self):
        return JNoseUp()


@valid_block
class JNoseDown(J):
    _shape = [(0, 0), (-1, 0), (1, 0), (1, 1)]

    def _next(self):
        return JNoseLeft()

    def _previous(self):
        return JNoseRight()


@valid_block
class JNoseLeft(J):
    _shape = [(0, 0), (0, -1), (0, 1), (-1, 1)]

    def _next(self):
        return JNoseUp()

    def _previous(self):
        return JNoseDown()


class L(Block):
    pass


@valid_block
class LNoseDown(L):
    _shape = [(0, 0), (1, 0), (-1, 0), (-1, 1)]

    def _next(self):
        return LNoseLeft()

    def _previous(self):
        return LNoseRight()


@valid_block
class LNoseLeft(L):
    _shape = [(0, 0), (0, 1), (0, -1), (-1, -1)]

    def _next(self):
        return LNoseUp()

    def _previous(self):
        return LNoseDown()


@valid_block
class LNoseUp(L):
    _shape = [(0, 0), (-1, 0), (1, 0), (1, -1)]

    def _next(self):
        return LNoseRight()

    def _previous(self):
        return LNoseLeft()


@valid_block
class LNoseRight(L):
    _shape = [(0, 0), (0, -1), (0, 1), (1, 1)]

    def _next(self):
        return LNoseDown()

    def _previous(self):
        return LNoseUp()


class T(Block):
    pass


@valid_block
class TNoseUp(T):
    _shape = [(0, 0), (0, -1), (-1, 0), (1, 0)]

    def _next(self):
        return TNoseRight()

    def _previous(self):
        return TNoseLeft()


@valid_block
class TNoseRight(T):
    _shape = [(0, 0), (1, 0), (0, -1), (0, 1)]

    def _next(self):
        return TNoseDown()

    def _previous(self):
        return TNoseUp()


@valid_block
class TNoseDown(T):
    _shape = [(0, 0), (0, 1), (-1, 0), (1, 0)]

    def _next(self):
        return TNoseLeft()

    def _previous(self):
        return TNoseRight()


@valid_block
class TNoseLeft(T):
    _shape = [(0, 0), (-1, 0), (0, 1), (0, -1)]

    def _next(self):
        return TNoseUp()

    def _previous(self):
        return TNoseDown()


class S(Block):
    pass


@valid_block
class SHorizontal(S):
    _shape = [(0, 0), (-1, 0), (0, -1), (1, -1)]

    def _next(self):
        return SVertical()

    def _previous(self):
        return SVertical()


@valid_block
class SVertical(S):
    _shape = [(0, 0), (0, -1), (1, 0), (1, 1)]

    def _next(self):
        return SHorizontal()

    def _previous(self):
        return SHorizontal()


class Z(Block):
    pass


@valid_block
class ZHorizontal(Z):
    _shape = [(0, 0), (1, 0), (0, -1), (-1, -1)]

    def _next(self):
        return ZVertical()

    def _previous(self):
        return ZVertical()


@valid_block
class ZVertical(Z):
    _shape = [(0, 0), (0, 1), (1, 0), (1, -1)]

    def _next(self):
        return ZHorizontal()

    def _previous(self):
        return ZHorizontal()


class U(Block):
    def __init__(self, err="Unknown"):
        self.err = err

    def __str__(self):
        return "%s - %s" % (self.__class__.__name__, self.err)


if __name__ == '__main__':
    print list(TNoseUp().rotations_clock_wise())
    print list(TNoseUp().rotations_counter_clock_wise())
    print list(O().rotations_clock_wise())
    print Block.get_random_block()
    # from game_objects.field import Field
    # from game_objects.control import Moveset

    # for b in Block.valid_blocks:
    #    print Field().add_block(b(), [Moveset.DROP])[0]
    #    print b()
