from which_pyqt import PYQT_VER

if PYQT_VER == "PYQT5":
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == "PYQT4":
    from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == "PYQT6":
    from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception("Unsupported Version of PyQt: {}".format(PYQT_VER))


import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):
    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert type(points) == list and type(points[0]) == QPointF

        t1 = time.time()
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        sorted_points = sorted(points, key=lambda point: point.x())
        t2 = time.time()

        t3 = time.time()
        polygon = self.convexHullWrapper(sorted_points)
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText("Time Elapsed (Convex Hull): {:3.3f} sec".format(t4 - t3))

    def convexHullWrapper(self, points):
        n = len(points)
        if len(points) <= 3:
            polygon = []
            for i in range(n):
                if i == n - 1:
                    polygon.append(QLineF(points[i], points[0]))
                else:
                    polygon.append(QLineF(points[i], points[i + 1]))
            return polygon

        left = points[: n // 2]
        right = points[n // 2 :]
        left_polygon = self.convexHullWrapper(left)
        right_polygon = self.convexHullWrapper(right)

        return self.mergePolygons(left_polygon, right_polygon)

    def mergePolygons(left_polygon, right_polygon):
        convex = []
        leftSide = max(left_polygon, key=lambda edge: edge.p2().x())
        rightSide = min(right_polygon, key=lambda edge: edge.p1().x())

        upperTangent = QLineF(leftSide, rightSide)
        return convex
