import pyautogui


class Moveset:
    LEFT, RIGHT, ROTATE, DROP = range(4)

    @staticmethod
    def to_str_list(list):
        result = ""
        for m in list:
            if m == Moveset.LEFT:
                result += "Left, "
            elif m == Moveset.RIGHT:
                result += "Right, "
            elif m == Moveset.ROTATE:
                result += "Rotate, "
            elif m == Moveset.DROP:
                result += "Drop, "
        return "'"+result[:-2]+"'"


class Controller:
    def __init__(self, left="left", right="right", rotate="up", drop=" ", key_pause=0.1):
        self._left = left
        self._right = right
        self._rotate = rotate
        self._drop = drop
        self._key_pause = key_pause

    def moveset_to_key(self, moveset):
        # type: (Moveset)-> str
        if moveset == Moveset.LEFT:
            return self._left
        elif moveset == Moveset.RIGHT:
            return self._right
        elif moveset == Moveset.ROTATE:
            return self._rotate
        elif moveset == Moveset.DROP:
            return self._drop
        else:
            return ""

    def move_block(self, moves):
        # type: (list)-> None
        if moves and len(moves) > 0:
            keys = [self.moveset_to_key(m) for m in moves]
            pyautogui.press(keys=keys, interval=self._key_pause)
