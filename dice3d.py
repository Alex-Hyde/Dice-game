import pygame
import math
import random

pygame.init()

win = pygame.display.set_mode((800, 600))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


def init(win_width=800, win_height=600):
    global win
    win = pygame.display.set_mode((win_width, win_height))


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def convert(self, currentCube, zChange=0):
        return int((self.x / (self.z + zChange)) * currentCube[2] + currentCube[0]), int((self.y / (self.z + zChange)) * currentCube[2] + currentCube[1])

    def spin(self, center, d):
        o = self.y - center.y
        a = self.x - center.x
        h = math.sqrt(o ** 2 + a ** 2)
        angle = math.degrees(math.atan(o / a + 0.0001))
        if a < 0:
            angle += 180
        self.y = h * math.sin(math.radians(angle + d))
        self.x = h * math.cos(math.radians(angle + d))

    def draw(self, currentCube, color=BLACK, size=2):
        pygame.draw.circle(win, color, self.convert(currentCube), size)

    def __truediv__(self, cons):
        return Point(self.x / cons, self.y / cons, self.z / cons)

    def __sub__(self, point):
        return Point(self.x - point.x, self.y - point.y, self.z - point.z)

    def dot(self, point):
        return self.x * point.x + self.y * point.y + self.z * point.z

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y, self.z + point.z)

    def __mul__(self, cons):
        return Point(self.x * cons, self.y * cons, self.z * cons)

    def distance(self, point):
        return math.sqrt((point.x - self.x) ** 2 + (point.y - self.y) ** 2 + (point.z - self.z) ** 2)

    def __str__(self):
        return str(self.x) + " ," + str(self.y) + " ," + str(self.z)

    def spin3d(self, point, line, degree=1):
        dy = (point - self) / -self.distance(point)
        dz = line.unit()
        dx = Point(dz.y * dy.z - dz.z * dy.y, dz.z * dy.x - dz.x * dy.z, dz.x * dy.y - dz.y * dy.x)
        #        point.draw(RED)
        #        Line(point + dy, point).draw(RED)
        #        Line(point + dz, point).draw(BLUE)
        #        Line(point + dx,point).draw(GREEN)
        vecPoint = point - self
        vy = vecPoint.dot(dy)
        vz = vecPoint.dot(dz)
        vx = vecPoint.dot(dx)
        vy, vx = spin(vy, vx, Point(0, 0, 0), 180 + degree)
        ndy = dy * vy
        ndz = dz * vz
        ndx = dx * vx

        newVec = ndy + ndz + ndx

        newPoint = newVec + point

        self.x = newPoint.x
        self.y = newPoint.y
        self.z = newPoint.z


class Line:
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2

    def closestPoint(self, point):
        d = (self.p2 - self.p1) / self.p2.distance(self.p1)
        v = point - self.p1
        t = v.dot(d)
        P = self.p1 + (d * t)
        return P

    # def draw(self, color=BLACK):
    #     pygame.draw.line(win, color, self.p1.convert(), self.p2.convert(), 2)

    def unit(self):
        return (self.p2 - self.p1) / self.p1.distance(self.p2)


class Side:
    def __init__(self, shapeList):
        self.shapes = shapeList

    def spin(self, line, degree):
        for shape in self.shapes:
            for point in shape:
                point.spin3d(line.closestPoint(point), line, degree)

    def convertPoly(self, index, pov):
        return [point.convert(pov) for point in self.shapes[index]]

    def draw(self, pov):
        for s in range(len(self.shapes)):
            pygame.draw.polygon(win, BLACK, self.convertPoly(s, pov))


class Shape:
    def __init__(self, points, connections, sides, sideImages, middle):
        self.points = points
        self.connections = connections
        self.sides = sides
        self.line = Line(middle, Point(1, 1, 10))
        self.middle = middle
        self.sideImages = sideImages
        self.rollValue = None
        self.spinSpeed = None
        self.index = None
        self.indexTotal = None
        self.landDelay = None
        self.spinIters = None
        self.counter = None
        self.pov = None
        self.rolling = True

    def draw(self):
        for i, side in enumerate(self.sides):
            if self.isVisible(side):
                self.drawSide(side)
                self.sideImages[i].draw(self.pov)

    def drawSide(self, side):
        pList = [self.points[p].convert(self.pov) for p in side]
        pygame.draw.polygon(win, WHITE, pList)
        pygame.draw.polygon(win, BLACK, pList, 2)

    def isVisible(self, side, zChange=0):
        pList = [self.points[point].convert(self.pov, zChange) for point in side]
        p1 = pList[0]
        p2 = pList[1]
        p3 = pList[2]
        p = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0]))
        if p > 0:
            return True
        else:
            return False

    def spinLine(self, degree):
        self.line.p2.x, self.line.p2.z = spin2(self.line.p2.x, self.line.p2.z, self.middle.x, self.middle.z, degree)

    def spin(self, degree):
        if self.line is not None:
            # self.spinLine(5)
            for point in self.points:
                point.spin3d(self.line.closestPoint(point), self.line, degree)
            for side in self.sideImages:
                side.spin(self.line, degree)

    def findLowest(self):
        lowest = None
        for point in self.points:
            if lowest is None:
                lowest = point
            elif lowest.y < point.y:
                lowest = point
        return lowest

    def groundHit(self):
        lowest = self.findLowest()
        vertLine = Line(self.middle, Point(self.middle.x, self.middle.y - 1, self.middle.z))
        point = vertLine.closestPoint(lowest)
        dy = (point - lowest) / -lowest.distance(point)
        dz = vertLine.unit()
        dx = Point(dz.y * dy.z - dz.z * dy.y, dz.z * dy.x - dz.x * dy.z, dz.x * dy.y - dz.y * dy.x)
        self.line = Line(self.middle, self.middle + dx)

    def roll(self):
        self.counter += 1
        self.rolling = True

        if self.index <= self.indexTotal:
            self.spin(self.spinSpeed)
        elif self.index <= self.indexTotal + self.spinIters + self.landDelay:
            if self.indexTotal + self.landDelay < self.index:
                self.line = Line(self.middle, self.middle + Point(1, 0, 0))
                self.spin(-90 / self.spinIters)
            self.index += 1
        else:
            for side in self.sides:
                if self.isVisible(side):
                    self.rollValue = self.sides.index(side) + 1
                    self.rolling = False

        if self.counter >= bounceTimer(self.index) and self.index <= 25:
            self.groundHit()
            self.index += 1
            self.counter = 0

    def get_roll_value(self):
        for side in self.sides:
            if self.isVisible(side, -5):
                return self.sides.index(side) + 1


def spin(py, px, center, d):
    o = py - center.y
    a = px - center.x
    h = math.sqrt(o ** 2 + a ** 2)
    angle = math.degrees(math.atan(o / (a + 0.00000001)))
    #        if a < 0:
    #            angle += 180
    py = h * math.sin(math.radians(angle + d))
    px = h * math.cos(math.radians(angle + d))
    return py, px


def spin2(px, py, cx, cy, d):
    o = py - cy
    a = px - cx
    h = math.sqrt(o ** 2 + a ** 2)
    angle = math.degrees(math.atan(o / (a + 0.00000001)))
    if a < 0:
        angle += 180
    npy = h * math.sin(math.radians(angle + d))
    npx = h * math.cos(math.radians(angle + d))
    return cx + npx, cy + npy


def redraw():
    pygame.display.update()
    win.fill(WHITE)


def createDot(x, y, axis, cons):
    size = 0.4
    if axis == "z":
        return [Point(x, y, cons), Point(x - size, y, cons), Point(x - size, y - size, cons), Point(x, y - size, cons)]
    elif axis == "x":
        return [Point(cons, y, x + 10), Point(cons, y, x - size + 10), Point(cons, y - size, x - size + 10), Point(cons, y - size, x + 10)]
    elif axis == "y":
        return [Point(x, cons, y + 10), Point(x - size, cons, y + 10), Point(x - size, cons, y - size + 10), Point(x, cons, y - size + 10)]


def bounceTimer(x):
    return 1 * (((x - 25) / 5) ** 2)


def createCube(x, y, zoom):
    cube = Shape([Point(1, 1, 9), Point(1, -1, 9), Point(-1, -1, 9), Point(-1, 1, 9), Point(1, 1, 11), Point(1, -1, 11),
                  Point(-1, -1, 11), Point(-1, 1, 11)],
                 [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 5), (2, 6), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4)],
                 [(0, 1, 2, 3), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0), (4, 7, 6, 5)],
                 [Side([createDot(0.2, 0.2, "z", 9)]),
                  Side([createDot(0.7, 0.7, "x", 1), createDot(-0.3, -0.3, "x", 1)]),
                  Side([createDot(0.8, 0.8, "y", -1), createDot(0.2, 0.2, "y", -1), createDot(-0.4, -0.4, "y", -1)]),
                  Side([createDot(0.7, 0.7, "x", -1), createDot(-0.3, 0.7, "x", -1),
                        createDot(-0.3, -0.3, "x", -1), createDot(0.7, -0.3, "x", -1)]),
                  Side([createDot(0.8, 0.8, "y", 1), createDot(0.8, -0.4, "y", 1), createDot(-0.4, -0.4, "y", 1),
                        createDot(-0.4, 0.8, "y", 1), createDot(0.2, 0.2, "y", 1)]),
                  Side([createDot(0.7, 0.8, "z", 11), createDot(0.7, 0.2, "z", 11), createDot(0.7, -0.4, "z", 11),
                        createDot(-0.3, 0.8, "z", 11), createDot(-0.3, 0.2, "z", 11), createDot(-0.3, -0.4, "z", 11)])],
                 Point(0, 0, 10))

    cube.pov = x, y, zoom

    cube.index = 1
    cube.indexTotal = 25
    cube.landDelay = 20
    cube.spinIters = 30

    cube.counter = 0

    cube.spinSpeed = random.randrange(3, 11)

    start = random.randrange(6)
    if start < 4:
        cube.line = Line(cube.middle, Point(0, 1, 10))
        cube.spin(90 * start)
    elif start == 4:
        cube.line = Line(cube.middle, Point(1, 0, 10))
        cube.spin(90)
    elif start == 5:
        cube.line = Line(cube.middle, Point(1, 0, 10))
        cube.spin(-90)

    cube.line = Line(cube.middle, Point(1, 1, 10))

    return cube
