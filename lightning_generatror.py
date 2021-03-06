# coding=utf-8
# reference: http://drilian.com/2009/02/25/lightning-bolts
# reference: https://stackoverflow.com/questions/16890711/normalise-and-perpendicular-function-in-python
# reference: https://gamedevelopment.tutsplus.com/tutorials/how-to-generate-shockingly-good-2d-lightning-effects--gamedev-2681
# reference: http://www.mrcolson.com/2015/12/20/Simulating-Lightning-with-Python.html

import math
import random
from PIL import Image, ImageDraw


class LightningBolt(object):
    def __init__(self, segments, intensity = 2):
        self.segments = segments
        self.intensity = intensity


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

    def __div__(self, factor):
        # division factor must be a number
        assert isinstance(factor, (int, long, float, complex))
        return Coord(self.x / factor, self.y / factor)

    def __repr__(self):
        # Used to get human readable coordinates when printing
        return "Coord(%f,%f)" % (self.x, self.y)

    def length(self):
        # Returns the length of the vector
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def angle(self):
        # Returns the vector's angle
        return math.atan2(self.y, self.x)

    def normalize(self):
        return self / self.length()


def rotate_counter_clockwise(coord, rad_angle):
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


def to_quadruple(segment):
    start, end = segment
    return start.x, start.y, end.x, end.y


GIF_FRAMES_CNT = 50
MAX_OFFSET = 100  # max offset from a lightning vertex
LIGHTNING_COLOR = (250, 251, 165)


def generate_single_bolt(origin, tail):
    segments = [(origin, tail)]
    offset = MAX_OFFSET
    # figure out a reasonable number of refinement rounds for the lightning to look real
    refinement_limit = int((tail - origin).length() / 80)

    for _ in xrange(0, refinement_limit):
        new_segments = []

        for segment in segments:
            start, end = segment
            mid = (start + end) / 2

            # give the current segment a slight twist along the perpendicular direction
            # 90 deg = pi/2 https://www.shodor.org/os411/courses/411a/module01/unit02/vector_degr.html
            perpendicular = rotate_counter_clockwise((end - start).normalize(), math.pi / 2)
            adjustment = random.uniform(-offset, offset)

            mid += perpendicular * adjustment
            new_segments.append((start, mid))
            new_segments.append((mid, end))

        segments = new_segments
        offset = offset / 2  # gradually reduce the adjustment effect

    return LightningBolt(segments)


def generate_lightnings():
    lightning_origin_x = random.randint(10, 300)
    lightning_origin = Coord(lightning_origin_x, 10)
    lightning_tail = Coord(lightning_origin_x + random.randint(500, 700), 500)

    lightnings = []
    main_bolt = generate_single_bolt(lightning_origin, lightning_tail)
    main_bolt.intensity = 3
    lightnings.append(main_bolt)

    branch_cnt = random.randint(3, 6)
    branch_pts = random.sample(set(main_bolt.segments), branch_cnt)
    for start, end in branch_pts:
        branch_origin = end

        rotation = random.choice([-1, 1]) * math.pi / 6  # +/-30 deg
        # this an intentional choice to use (lightning_origin, end) as the rotation baseline
        # if we used (start, end) as a baseline, the segment is too tiny and the branch's rotation
        # tend to become totally off
        direction = rotate_counter_clockwise((end - lightning_origin).normalize(), rotation)
        magnitude = (lightning_tail - branch_origin).length()

        branch_end = branch_origin + direction * magnitude
        lightnings.append(generate_single_bolt(branch_origin, branch_end))

    return lightnings


def draw_lightnings(background, lightnings):
    draw = ImageDraw.Draw(background)

    for lightning in lightnings:
        for segment in lightning.segments:
            draw.line(to_quadruple(segment), fill=LIGHTNING_COLOR, width=lightning.intensity)


def main():
    background = Image.open("rainy_sky.jpg")
    frames = []

    for i in xrange(0, GIF_FRAMES_CNT):
        # make a copy of the background for new drawings
        frame = background.copy()
        draw_lightnings(frame, generate_lightnings())
        frames.append(frame)
        # add empty background for flashing lightning effect
        frames.append(background)

    background.save(fp='thor.gif', format='gif', save_all=True, append_images=frames)


if __name__ == "__main__":
    main()
