import threading

import time

from areas import SIZE, Areas
from analyse import Analyser
from moushandling import MouseHandler, calc_region_of_clicks
from screenshothandling import ScreenshotHandler
from game_objects import blocks


class BoardMonitor:
    _callbacks = list()

    @staticmethod
    def register_block_callback(func):
        BoardMonitor._callbacks.append(func)

    def __init__(self, field_width=10, field_region=None, next_region=None):
        mouse = MouseHandler()
        threading.Thread(target=mouse.run).start()
        if field_region is None:
            print "Click on the top left and afterwards on the bottom right of the gamefield"
            while not len(mouse.get_clicks()) > 1:
                time.sleep(0.1)
            field_clicks = mouse.get_clicks()
            field_region = calc_region_of_clicks(field_clicks[0], field_clicks[1])
            mouse.clear_clicks()
            print "field_region", field_region
        if next_region is None:
            print "Click on the top left and afterwards on the bottom right of the next area"
            while not len(mouse.get_clicks()) > 1:
                time.sleep(0.1)
            next_clicks = mouse.get_clicks()
            next_region = calc_region_of_clicks(next_clicks[0], next_clicks[1])
            mouse.clear_clicks()
            print "next_region", next_region
        mouse.halt()

        self._screenshot_handler = ScreenshotHandler()
        self._screenshot_handler.register_region(Areas.FIELD, field_region)
        self._screenshot_handler.register_region(Areas.NEXT, next_region)

        self._analyser = Analyser(field_region[2] / field_width)

        self._is_running = False
        self._current = blocks.U()
        self._next = blocks.U()

    def halt(self):
        self._is_running = False

    def get_field_block(self):
        field_img = self._screenshot_handler.take_screenshot(Areas.FIELD)
        field_img = field_img.crop((0, 0, field_img.width, field_img.height / 3))
        return self._analyser.get_shape(field_img, crop_bottom=True)

    def get_next_block(self):
        next_img = self._screenshot_handler.take_screenshot(Areas.NEXT)
        return self._analyser.get_shape(next_img)

    def push(self):
        self._is_running = True
        print "searching for the blocks"
        while self._is_running:
            start = time.time()
            detected_current = self.get_field_block()
            detected_next = self.get_next_block()
            if not detected_current.is_unknown() and not detected_next.is_unknown() \
                    and (not detected_current.same_type(self._current) or not detected_next.same_type(self._next)):
                if not self._next.is_unknown() and not detected_current.same_type(self._next):
                    continue
                self._current = detected_current
                self._next = detected_next
                print int(1000 * (time.time() - start)), self._current, self._next
                for c in self._callbacks:
                    c(detected_current, detected_next)

    def push_wait(self):
        self._is_running = True
        print "searching for the blocks"
        while self._is_running:
            start = time.time()
            detected_current = self.get_field_block()
            detected_next = self.get_next_block()
            #print detected_current, detected_next
            if not detected_current.is_unknown() and not detected_next.is_unknown():
                if not self._next.is_unknown() and not detected_current.same_type(self._next):
                    continue
                self._next = detected_next
                for c in self._callbacks:
                    c(detected_current, detected_next)
                print "%sms current: %s next:%s" % (int(1000 * (time.time() - start)), detected_current, detected_next)

    def pull(self):
        # type: (None) -> (blocks.Block, blocks.Block)
        if self._current.is_unknown():
            self._current = self.get_field_block()
            print self._current
        else:
            self._current = self._next
        self._next = self.get_next_block()
        return self._current, self._next
