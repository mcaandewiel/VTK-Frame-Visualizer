#   @author Christian aan de Wiel
#   Color Mapper Module
#   Based on: https://stackoverflow.com/questions/876853/generating-color-ranges-in-python

import colorsys

class ColorMapper():
    def __init__(self, n):
        self.index = -1
        HSV_tuples = [(x * 1.0 / n, 1.0, 1.0) for x in range(n)]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
    
    def getCurrent(self):
        if self.index == -1:
            return self.colors[0]

        return self.colors[self.index]

    def getNext(self):
        self.index = min(self.index + 1, len(self.colors) - 1)

        return self.colors[self.index]
