import cv2
import math

# ----------------------------------------------------------------------------------------------------------------------------
# KONSTANTE
# ----------------------------------------------------------------------------------------------------------------------------
# dimenzije rezolucije kamere i prozora
# USB 2.1 						USB 3.0
cameraCaptureResolutionX = 1280	# 1920
cameraCaptureResolutionY = 720	# 1080
cameraCaptureFps = 15 			# 30
windowWidth = 800

# tipovi, udaljenosti i vrijednosti markera
arucoType = cv2.aruco.DICT_4X4_1000
markerSideLength = 0.03
markerDiagonalLength = round(math.sqrt((markerSideLength ** 2) * 2), 4)
markerOrientationLength = 0.015
corner1ID = measuringMarkerID = 0
corner2ID = 1
corner3ID = 2

# boje
blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
yellow = (0, 255, 255)

# mjere linija pomocu kojih se crta po ekranu
lineWidth = 2
circleWidth = -1
circleRadius = 4
borderCircleWidth = 2
borderCircleRadius = 5

# razne udaljenosti
focusedTrackScreenMargin = 40
centerSquareSideLength = 15