import re
import math
from collections import OrderedDict

reg = "^\\[(\\d\\d):(\\d\\d).(\\d{2,3})](.*)"


def lower(lst, val):
    for i in range(len(lst)):
        if lst[i] > val:
            if i - 1 < 0:
                return -1
            return lst[i - 1]
    return lst[len(lst) - 1]


class LrcParser:
    def __init__(self, file) -> None:
        self.map = OrderedDict()
        self.file = file
        self.read()

    def read(self):
        with open(self.file, encoding='utf-8') as lrc:
            line = lrc.readline()
            while line != '':
                match = re.match(reg, line.strip())
                if match is not None:
                    time = (int(match.group(1)) * 60 + int(match.group(2)) +
                            int(match.group(3)) /
                            math.pow(10, len(match.group(3))))
                    if time not in self.map:
                        self.map[time] = []
                    self.map[time].append(match.group(4))
                line = lrc.readline()

    def get(self, time):
        key = lower(list(self.map.keys()), time)
        if key < 0:
            return (-1, [])
        return key, self.map[key]
