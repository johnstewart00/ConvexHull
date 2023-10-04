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
        # print("sorted points: ", sorted_points)
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
            if n == 1:
                polygon.append(QLineF(points[0], points[0]))
            elif n == 2:
                polygon.append(QLineF(points[0], points[1]))
            else:
                for i in range(n):
                    if i == 2:
                        polygon.append(QLineF(points[i], points[0]))
                    else:
                        polygon.append(QLineF(points[i], points[i + 1]))
            return polygon

        left = points[: n // 2]
        right = points[n // 2 :]
        left_polygon = self.convexHullWrapper(left)
        right_polygon = self.convexHullWrapper(right)
        print("left polygon size is: ", len(left_polygon))
        print("right polygon size is: ", len(right_polygon))
        return self.mergePolygons(left_polygon, right_polygon)

    def mergePolygons(self, left_polygon, right_polygon):
        convex = []
        leftPolygonPoints = []
        rightPolygonPoints = []

        # get all points from the left polygon
        for i in range(len(left_polygon)):
            if left_polygon[i].p1() in leftPolygonPoints:
                if left_polygon[i].p2() in leftPolygonPoints:
                    continue
                else:
                    leftPolygonPoints.append(left_polygon[i].p2())
                    continue
            leftPolygonPoints.append(left_polygon[i].p1())
            if left_polygon[i].p2() in leftPolygonPoints:
                continue
            else:
                leftPolygonPoints.append(left_polygon[i].p2())

        # get all points from the right polygon
        for i in range(len(right_polygon)):
            if right_polygon[i].p1() in rightPolygonPoints:
                if right_polygon[i].p2() in rightPolygonPoints:
                    continue
                else:
                    rightPolygonPoints.append(right_polygon[i].p2())
                    continue
            rightPolygonPoints.append(right_polygon[i].p1())
            if right_polygon[i].p2() in rightPolygonPoints:
                continue
            else:
                rightPolygonPoints.append(right_polygon[i].p2())

        # give convex the entire two polygons
        for i in range(len(left_polygon)):
            convex.append(left_polygon[i])
        for i in range(len(right_polygon)):
            convex.append(right_polygon[i])

        leftVertex = leftPolygonPoints[0]
        for i in range(len(leftPolygonPoints)):
            if leftPolygonPoints[i].x() > leftVertex.x():
                leftVertex = leftPolygonPoints[i]
        rightVertex = rightPolygonPoints[0]
        for i in range(len(rightPolygonPoints)):
            if rightPolygonPoints[i].x() < rightVertex.x():
                rightVertex = rightPolygonPoints[i]

        print("leftVertex is: ", leftVertex)
        print("rightVertex is: ", rightVertex)

        delta_x = rightVertex.x() - leftVertex.x()
        delta_y = rightVertex.y() - leftVertex.y()

        # Calculate the slope
        slope = delta_y / delta_x
        print(slope)

        # get the upper tangent
        leftVertexCopy = leftVertex
        rightVertexCopy = rightVertex
        slopeCopy = slope
        # get the top of the right polygon
        rightVertexCopy, didChange, slopeCopy = self.getTopOfRightPolygon(
            rightPolygonPoints, rightVertexCopy, leftVertexCopy, slopeCopy
        )
        print("top of right polygon is: ", rightVertex)
        # get the top of the left polygon
        leftVertexCopy, didChange, slopeCopy = self.getTopOfLeftPolygon(
            leftPolygonPoints, leftVertexCopy, rightVertexCopy, slopeCopy
        )
        print("top of left polygon is: ", leftVertexCopy)
        while didChange:
            rightVertexCopy, didChange, slopeCopy = self.getTopOfRightPolygon(
                rightPolygonPoints, rightVertexCopy, leftVertexCopy, slopeCopy
            )
            leftVertexCopy, didChange, slopeCopy = self.getTopOfLeftPolygon(
                leftPolygonPoints, leftVertexCopy, rightVertexCopy, slopeCopy
            )
        print("the upper tangent should be: ", leftVertexCopy, " ", rightVertexCopy)
        convex.append(QLineF(leftVertexCopy, rightVertexCopy))

        # get the lower tangent
        # get the bottom of the right polygon
        rightVertex, didChange, slope = self.getBottomOfRightPolygon(
            rightPolygonPoints, rightVertex, leftVertex, slope
        )
        # get the bottom of the left polygon
        leftVertex, didChange, slope = self.getBottomOfLeftPolygon(
            leftPolygonPoints, leftVertex, rightVertex, slope
        )
        while didChange:
            rightVertex, didChange, slope = self.getBottomOfRightPolygon(
                rightPolygonPoints, rightVertex, leftVertex, slope
            )
            leftVertex, didChange, slope = self.getBottomOfLeftPolygon(
                leftPolygonPoints, leftVertex, rightVertex, slope
            )
        print("bottom of right polygon is: ", rightVertex)
        print("bottom of left polygon is: ", leftVertex)

        print("the lower tangent should be: ", leftVertex, " ", rightVertex)
        convex.append(QLineF(leftVertex, rightVertex))

        # remove lines inbetween the two tangents
        return convex

    def getTopOfRightPolygon(
        self, rightPolygonPoints, rightVertexCopy, leftVertexCopy, slopeCopy
    ):
        didChange = False
        for a in range(len(rightPolygonPoints)):
            newRight = rightPolygonPoints[a]
            if newRight == rightVertexCopy:
                continue
            delta_x = newRight.x() - leftVertexCopy.x()
            delta_y = newRight.y() - leftVertexCopy.y()
            newSlope = delta_y / delta_x
            if newSlope > slopeCopy:
                rightVertexCopy = newRight
                slopeCopy = newSlope
                didChange = True
            elif newSlope == slopeCopy:
                if newRight.y() > rightVertexCopy.y():
                    rightVertexCopy = newRight
        return rightVertexCopy, didChange, slopeCopy

    def getTopOfLeftPolygon(
        self, leftPolygonPoints, leftVertexCopy, rightVertexCopy, slopeCopy
    ):
        didChange = False
        for b in range(len(leftPolygonPoints)):
            newLeft = leftPolygonPoints[b]
            if newLeft == leftVertexCopy:
                continue
            delta_x = rightVertexCopy.x() - newLeft.x()
            delta_y = rightVertexCopy.y() - newLeft.y()
            newSlope = delta_y / delta_x
            if newSlope < slopeCopy:
                leftVertexCopy = newLeft
                slopeCopy = newSlope
                didChange = True
            elif newSlope == slopeCopy:
                if newLeft.y() > leftVertexCopy.y():
                    leftVertexCopy = newLeft
        return leftVertexCopy, didChange, slopeCopy

    def getBottomOfRightPolygon(
        self, rightPolygonPoints, rightVertex, leftVertex, slope
    ):
        didChange = False
        for c in range(len(rightPolygonPoints)):
            newRight = rightPolygonPoints[c]
            if newRight == rightVertex:
                continue
            delta_x = newRight.x() - leftVertex.x()
            delta_y = newRight.y() - leftVertex.y()
            newSlope = delta_y / delta_x
            if newSlope < slope:
                rightVertex = newRight
                slope = newSlope
                didChange = True
            elif newSlope == slope:
                if newRight.y() < rightVertex.y():
                    rightVertex = newRight
        return rightVertex, didChange, slope

    def getBottomOfLeftPolygon(self, leftPolygonPoints, leftVertex, rightVertex, slope):
        didChange = False
        for d in range(len(leftPolygonPoints)):
            newLeft = leftPolygonPoints[d]
            if newLeft == leftVertex:
                continue
            delta_x = rightVertex.x() - newLeft.x()
            delta_y = rightVertex.y() - newLeft.y()
            newSlope = delta_y / delta_x
            if newSlope > slope:
                leftVertex = newLeft
                slope = newSlope
                didChange = True
            elif newSlope == slope:
                if newLeft.y() < leftVertex.y():
                    leftVertex = newLeft
        return leftVertex, didChange, slope
