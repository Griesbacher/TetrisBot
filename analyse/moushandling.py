from pymouse import PyMouseEvent


# Does not work on second screen
class MouseHandler(PyMouseEvent):
    _clicks = list()
    _finished = False

    def __init__(self):
        PyMouseEvent.__init__(self)
        self.setDaemon(True)

    def click(self, x, y, button, press):
        if button == 1 and press and not self._finished:
            self._clicks.append([x, y])
        elif button == 2:
            self.halt()

    def scroll(self, vertical=None, horizontal=None, depth=None):
        pass

    def halt(self):
        self._finished = True
        self.stop()

    def get_clicks(self):
        return self._clicks

    def clear_clicks(self):
        self._clicks = list()


def calc_region_of_clicks(c1, c2):
    return c1[0], c1[1], c2[0] - c1[0], c2[1] - c1[1]
