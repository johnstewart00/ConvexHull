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
PAUSE = 1


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
            if n == 1:
                polygon.append(QLineF(points[0], points[0]))
            elif n == 2:
                polygon.append(QLineF(points[0], points[1]))
                polygon.append(QLineF(points[1], points[0]))
            else:
                if self.calculateSlope(points[0], points[1]) > self.calculateSlope(
                    points[0], points[2]
                ):
                    polygon.append(QLineF(points[0], points[1]))
                    polygon.append(QLineF(points[1], points[2]))
                    polygon.append(QLineF(points[2], points[0]))
                else:
                    polygon.append(QLineF(points[0], points[2]))
                    polygon.append(QLineF(points[2], points[1]))
                    polygon.append(QLineF(points[1], points[0]))
            return polygon

        left = points[: n // 2]
        right = points[n // 2 :]
        left_polygon = self.convexHullWrapper(left)
        right_polygon = self.convexHullWrapper(right)
        return self.mergePolygons(left_polygon, right_polygon)

    def mergePolygons(self, left_polygon, right_polygon):
        convex = []
        leftPolygonPoints = self.getPoints(left_polygon)
        rightPolygonPoints = self.getPoints(right_polygon)

        # give convex the entire two polygons
        for i in range(len(left_polygon)):
            if left_polygon[i] in convex:
                continue
            convex.append(left_polygon[i])
        for i in range(len(right_polygon)):
            if right_polygon[i] in convex:
                continue
            convex.append(right_polygon[i])

        leftVertex = leftPolygonPoints[0]
        for i in range(len(leftPolygonPoints)):
            if leftPolygonPoints[i].x() > leftVertex.x():
                leftVertex = leftPolygonPoints[i]
        rightVertex = rightPolygonPoints[0]
        for i in range(len(rightPolygonPoints)):
            if rightPolygonPoints[i].x() < rightVertex.x():
                rightVertex = rightPolygonPoints[i]

        # Calculate the slope
        slope = self.calculateSlope(leftVertex, rightVertex)
        # get the upper tangent
        leftVertexCopy = leftVertex
        rightVertexCopy = rightVertex
        slopeCopy = slope
        # get the top of the right polygon
        rightVertexCopy, didChange, slopeCopy, convex = self.getTopOfRightPolygon(
            len(rightPolygonPoints),
            rightVertexCopy,
            leftVertexCopy,
            slopeCopy,
            convex,
            right_polygon,
        )
        # get the top of the left polygon
        leftVertexCopy, didChange, slopeCopy, convex = self.getTopOfLeftPolygon(
            len(leftPolygonPoints),
            leftVertexCopy,
            rightVertexCopy,
            slopeCopy,
            convex,
            left_polygon,
        )
        while didChange:
            rightVertexCopy, didChange, slopeCopy, convex = self.getTopOfRightPolygon(
                len(rightPolygonPoints),
                rightVertexCopy,
                leftVertexCopy,
                slopeCopy,
                convex,
                right_polygon,
            )
            leftVertexCopy, didChange, slopeCopy, convex = self.getTopOfLeftPolygon(
                len(leftPolygonPoints),
                leftVertexCopy,
                rightVertexCopy,
                slopeCopy,
                convex,
                left_polygon,
            )
        upperTangent = QLineF(leftVertexCopy, rightVertexCopy)

        # get the lower tangent
        # get the bottom of the right polygon
        rightVertex, didChange, slope, convex = self.getBottomOfRightPolygon(
            len(rightPolygonPoints),
            rightVertex,
            leftVertex,
            slope,
            convex,
            right_polygon,
        )
        # get the bottom of the left polygon
        leftVertex, didChange, slope, convex = self.getBottomOfLeftPolygon(
            len(leftPolygonPoints), leftVertex, rightVertex, slope, convex, left_polygon
        )
        while didChange:
            rightVertex, didChange, slope, convex = self.getBottomOfRightPolygon(
                len(rightPolygonPoints),
                rightVertex,
                leftVertex,
                slope,
                convex,
                right_polygon,
            )
            leftVertex, didChange, slope, convex = self.getBottomOfLeftPolygon(
                len(leftPolygonPoints),
                leftVertex,
                rightVertex,
                slope,
                convex,
                left_polygon,
            )
        lowerTangent = QLineF(rightVertex, leftVertex)

        # find the right plave to add the  upper tangent
        upperIndex = 0
        for i in range(len(convex)):
            if convex[i].p2() == upperTangent.p1():
                upperIndex = i
        convex.insert(upperIndex + 1, upperTangent)
        lowerIndex = 0
        for i in range(len(convex)):
            if convex[i].p2() == lowerTangent.p1():
                lowerIndex = i
        convex.insert(lowerIndex + 1, lowerTangent)

        return convex

    def getTopOfRightPolygon(
        self,
        numPoints,
        rightVertexCopy,
        leftVertexCopy,
        slopeCopy,
        convex,
        rightPolygon,
    ):
        didChange = False
        for _ in range(numPoints):
            newRight = None
            for line in rightPolygon:
                if line.p1() == rightVertexCopy:
                    newRight = line.p2()
                    break
            newSlope = self.calculateSlope(newRight, leftVertexCopy)
            if newSlope > slopeCopy:
                convex = self.deleteLine(rightVertexCopy, newRight, convex)
                rightVertexCopy = newRight
                slopeCopy = newSlope
                didChange = True
        return rightVertexCopy, didChange, slopeCopy, convex

    def getTopOfLeftPolygon(
        self,
        numPoints,
        leftVertexCopy,
        rightVertexCopy,
        slopeCopy,
        convex,
        leftPolygon,
    ):
        didChange = False
        for _ in range(numPoints):
            newLeft = None
            for line in leftPolygon:
                if line.p2() == leftVertexCopy:
                    newLeft = line.p1()
                    break
            newSlope = self.calculateSlope(rightVertexCopy, newLeft)
            if newSlope < slopeCopy:
                convex = self.deleteLine(newLeft, leftVertexCopy, convex)
                leftVertexCopy = newLeft
                slopeCopy = newSlope
                didChange = True
        return leftVertexCopy, didChange, slopeCopy, convex

    def getBottomOfRightPolygon(
        self, numPoints, rightVertex, leftVertex, slope, convex, rightPolygon
    ):
        didChange = False
        for _ in range(numPoints):
            newRight = None
            for line in rightPolygon:
                if line.p2() == rightVertex:
                    newRight = line.p1()
                    break
            newSlope = self.calculateSlope(newRight, leftVertex)
            if newSlope < slope:
                convex = self.deleteLine(newRight, rightVertex, convex)
                rightVertex = newRight
                slope = newSlope
                didChange = True
        return rightVertex, didChange, slope, convex

    def getBottomOfLeftPolygon(
        self, numPoints, leftVertex, rightVertex, slope, convex, leftPolygon
    ):
        didChange = False
        for _ in range(numPoints):
            newLeft = None
            for line in leftPolygon:
                if line.p1() == leftVertex:
                    newLeft = line.p2()
                    break
            newSlope = self.calculateSlope(rightVertex, newLeft)
            if newSlope > slope:
                convex = self.deleteLine(leftVertex, newLeft, convex)
                leftVertex = newLeft
                slope = newSlope
                didChange = True
        return leftVertex, didChange, slope, convex

    def deleteLine(self, point1, point2, convex):
        for i in range(len(convex)):
            if convex[i].p1() == point1 and convex[i].p2() == point2:
                self.eraseTangent([convex[i]])
                del convex[i]
                return convex

        print("we should never be here")
        return convex

    def calculateSlope(self, rightVertex, leftVertex):
        delta_x = rightVertex.x() - leftVertex.x()
        delta_y = rightVertex.y() - leftVertex.y()
        return delta_y / delta_x

    def getPoints(self, polygon):
        points = []
        for i in range(len(polygon)):
            if polygon[i].p1() in points:
                if polygon[i].p2() in points:
                    continue
                else:
                    points.append(polygon[i].p2())
                    continue
            points.append(polygon[i].p1())
            if polygon[i].p2() in points:
                continue
            else:
                points.append(polygon[i].p2())
        return points
