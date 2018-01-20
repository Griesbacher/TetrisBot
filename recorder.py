import os
import pickle

import copy

from game_objects.field import NBlox

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Recorder:
    cache = {}

    def __init__(self, width, file_path=os.path.join(ROOT_DIR, "recorded_blocks.p")):
        # type: (int, str) -> None
        self._width = width
        self._file_path = file_path
        self._records = dict()
        if file_path not in Recorder.cache:
            if os.path.exists(file_path):
                old_records = pickle.load(open(file_path, "rb"))
                if old_records is not None:
                    self._records = old_records
                    Recorder.cache[file_path] = old_records
        else:
            self._records = Recorder.cache[file_path]
        if width not in self._records:
            self._records[width] = list()
        self._records[width].append(list())
        self._current_index = len(self._records[width]) - 1

    def rec_callback(self, current_block, next_block):
        self._records[self._width][self._current_index].append(current_block)
        if len(self._records[self._width][self._current_index]) % 5 == 0:
            print "Saving Blocks"
            self.write_down()

    def write_down(self):
        pickle.dump(self._records, open(self._file_path, "wb"))

    def play_recorded(self, width, rec_index=-1):
        if rec_index < 0:
            rec_index = len(self._records[width]) - 1
        current = None
        for r in self._records[width][rec_index]:
            if current is None:
                current = r
                continue
            yield current, r
            current = r

    def play_all_recorded(self, width):
        for i in range(len(self._records[width])):
            yield self.play_recorded(width, i)

    def play_all_at_once(self, width, reversed=False):
        sorted_records = sorted(self._records[width], key=lambda x: len(x), reverse=reversed)
        current = None
        for record in sorted_records:
            for b in record:
                if current is None:
                    current = b
                    continue
                yield current, b
                current = b


if __name__ == '__main__':
    # for b in Recorder(NBlox.get_width()).play_all(NBlox.get_width()):
    # print b
    print len(list(Recorder(NBlox.get_width()).play_all_at_once(NBlox.get_width())))
