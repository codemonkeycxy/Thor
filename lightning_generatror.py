# coding=utf-8
# reference: http://drilian.com/2009/02/25/lightning-bolts
# reference: https://stackoverflow.com/questions/16890711/normalise-and-perpendicular-function-in-python

import math
import random
from PIL import Image, ImageDraw


class Coord(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        # This allows you to subtract vectors
        return Coord(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __mul__(self, factor):
        # multiplication factor must be a number
        assert isinstance(factor, (int, long, float, complex))
        return Coord(self.x * factor, self.y * factor)

    def __rmul__(self, factor):
        return self.__mul__(factor)

    def __repr__(self):
        # Used to get human readable coordinates when printing
        return "Coord(%f,%f)" % (self.x, self.y)

    def length(self):
        # Returns the length of the vector
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def angle(self):
        # Returns the vector's angle
        return math.atan2(self.y, self.x)


def normalize(coord):
    return Coord(
        coord.x / coord.length(),
        coord.y / coord.length()
    )


def rotate(coord, rad_angle):
    # angle in radian: pi = 180 deg
    new_angle = coord.angle() + rad_angle

    # 2D vector rotation formula:
    # x' = x cos θ − y sin θ
    # y' = x sin θ + y cos θ
    # https://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
    return Coord(
        coord.x * math.cos(new_angle) - coord.y * math.sin(new_angle),
        coord.x * math.sin(new_angle) + coord.y * math.cos(new_angle)
    )


def find_mid(start, end):
    return Coord(
        (start.x + end.x) / 2,
        (start.y + end.y) / 2
    )


def to_quadruple(segment):
    start, end = segment
    return start.x, start.y, end.x, end.y


FIDELITY = 10  # larger number -> more realistic graphics -> slower rendering
MAX_OFFSET = 100  # max offset from a lightning vertex
BRANCH_LEN_SCALE = 0.7

LIGHTNING_COLOR = (250, 251, 165)
LIGHTNING_ORIGIN = Coord(10, 10)
LIGHTNING_TAIL = Coord(500, 500)


def main():
    background = Image.open("rainy_sky.jpg")
    draw = ImageDraw.Draw(background)

    segments = [(LIGHTNING_ORIGIN, LIGHTNING_TAIL)]
    offset = MAX_OFFSET
    for i in xrange(0, FIDELITY):
        new_segments = []

        for segment in segments:
            start, end = segment
            mid = find_mid(start, end)

            # give the current segment a slight twist along the perpendicular direction
            # 90 deg = pi/2 https://www.shodor.org/os411/courses/411a/module01/unit02/vector_degr.html
            perpendicular = rotate(normalize(end - start), math.pi / 2)
            adjustment = random.uniform(-offset, offset)

            mid += perpendicular * adjustment
            new_segments.append((start, mid))
            new_segments.append((mid, end))

        segments = new_segments
        offset = offset / 2  # gradually reduce the adjustment effect

    for segment in segments:
        draw.line(to_quadruple(segment), fill=LIGHTNING_COLOR)

    background.show()
    background.save('test.jpg', 'JPEG')


if __name__ == "__main__":
    main()
