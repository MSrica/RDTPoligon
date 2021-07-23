# TODO
# pretvoriti koordinate u tuplete/liste (globalne varijable)
# pretvoriti konstante u izmjenjive varijable (sirine linija itd.)
# convert drawCenterMeasuringSquare to drawCenterMeasuringCircle
# export function to other files


# KNJIZNICE
# ----------------------------------------------------------------------------------------------------------------------------
import pyrealsense2 as rs
import numpy as np
import imutils
import cv2
import math
import constants


# ----------------------------------------------------------------------------------------------------------------------------
# GLOBALNE VARIJABLE
# ----------------------------------------------------------------------------------------------------------------------------
# vrijednosti sredista markera
corner1X = corner1Y = corner2X = corner2Y = corner3X = corner3Y = calculatedCorner3X = calculatedCorner3Y = calculatedCorner4X = calculatedCorner4Y = 0

# matrice kamere
cameraMatrix = []
cameraDistortionCoefficients = []

# ????????????
rotated = None


# ----------------------------------------------------------------------------------------------------------------------------
# FUNKCIJE
# ----------------------------------------------------------------------------------------------------------------------------

# kamera
# ----------------------------------------------------------------------------------------------------------------------------
# pokretanje prijenosa podataka kamere
def pipelineInitilazation():
	pipeline = rs.pipeline()
	config = rs.config()
	config.enable_stream(rs.stream.color, constants.cameraCaptureResolutionX, constants.cameraCaptureResolutionY, rs.format.bgr8, constants.cameraCaptureFps)
	pipeline.start(config)
	return pipeline

# kalibracija kamere
def pipelineCalibration(pipeline):
	activeProfile = pipeline.get_active_profile()
	colorProfile = rs.video_stream_profile(activeProfile.get_stream(rs.stream.color))
	colorIntrinsics = colorProfile.get_intrinsics()
	cameraMatrix = [[colorIntrinsics.fx, 0, colorIntrinsics.ppx], [0, colorIntrinsics.fy, colorIntrinsics.ppy], [0, 0, 1]]
	return np.float32(cameraMatrix), np.float32(colorIntrinsics.coeffs)

# prijenos podataka u sliku
def pipelineToImage(pipeline):
	frames = pipeline.wait_for_frames()
	colorFrame = frames.get_color_frame()
	colorImage = np.asanyarray(colorFrame.get_data())
	colorImage = imutils.resize(colorImage, width=constants.windowWidth)
	return colorImage


# aruco
# ----------------------------------------------------------------------------------------------------------------------------
# nalazenje markera na slici
def findArucoMarkers(image):
	arucoDictionary = cv2.aruco.Dictionary_get(constants.arucoType)
	arucoParameters = cv2.aruco.DetectorParameters_create()
	(corners, ids, _) = cv2.aruco.detectMarkers(image, arucoDictionary, parameters=arucoParameters)
	rotationVector, translationVector, _ = cv2.aruco.estimatePoseSingleMarkers(corners, constants.markerSideLength, cameraMatrix, cameraDistortionCoefficients)
	return corners, ids, rotationVector, translationVector


# izracun varijabli
# ----------------------------------------------------------------------------------------------------------------------------
# dobivanje svih koordinata markera
def getMarkerCoordinates(corners):
	(topLeft, topRight, bottomRight, bottomLeft) = corners
	topRight = (int(topRight[0]), int(topRight[1]))
	bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
	bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
	topLeft = (int(topLeft[0]), int(topLeft[1]))

	centerX = int((topLeft[0] + bottomRight[0]) / 2.0)
	centerY = int((topLeft[1] + bottomRight[1]) / 2.0)

	return topLeft, topRight, bottomRight, bottomLeft, centerX, centerY

# postavljanje koordinata granica staze
def setTrackCorners(markerID, centerX, centerY):
	global corner1X, corner1Y, corner2X, corner2Y, corner3X, corner3Y

	if markerID == constants.corner1ID:
		corner1X = centerX
		corner1Y = centerY
	elif markerID == constants.corner2ID:
		corner2X = centerX
		corner2Y = centerY
	elif markerID == constants.corner3ID:
		corner3X = centerX
		corner3Y = centerY

# dobivanje koordinata fokusirane staze
def getFocusedTrackCoordinates(maxX, maxY):
	minCornerX = min(corner1X, corner2X, corner3X, calculatedCorner3X, calculatedCorner4X) - constants.focusedTrackScreenMargin
	minCornerY = min(corner1Y, corner2Y, corner3Y, calculatedCorner3Y, calculatedCorner4Y) - constants.focusedTrackScreenMargin
	maxCornerX = max(corner1X, corner2X, corner3X, calculatedCorner3X, calculatedCorner4X) + constants.focusedTrackScreenMargin
	maxCornerY = max(corner1Y, corner2Y, corner3Y, calculatedCorner3Y, calculatedCorner4Y) + constants.focusedTrackScreenMargin

	if minCornerX < 0: minCornerX = 1
	if minCornerY < 0: minCornerY = 1
	if maxCornerX > maxX: maxCornerX = maxX
	if maxCornerY > maxY: maxCornerY = maxY

	return minCornerX, minCornerY, maxCornerX, maxCornerY

# izracun 3. i 4. ugla
def calculateImaginaryBoundaries():
	global calculatedCorner3X, calculatedCorner3Y, calculatedCorner4X, calculatedCorner4Y

	# udaljenost izmedu linije i tocke 3
	realMarker1 = np.array([corner1X, corner1Y])
	realMarker2 = np.array([corner2X, corner2Y])
	realMarker3 = np.array([corner3X, corner3Y])
	corner3DistanceToLine = np.abs(np.cross(realMarker2 - realMarker1, realMarker1 - realMarker3)) / np.linalg.norm(realMarker2 - realMarker1)

	# vektor izmedu tocaka
	lineVector = list((corner2X - corner1X, corner2Y - corner1Y))

	# vektor izmedu c3 i c2
	dotVector = (corner2X - corner3X, corner2Y - corner3Y)
	
	# umnozak vektora za izracun orijentacije pravokutnika
	crossProduct = lineVector[0]*dotVector[1] - lineVector[1]*dotVector[0]
	rectangleOrientation = 1 if crossProduct < 0 else -1

	# normalizacija vektora
	lineLength = math.sqrt(lineVector[0]*lineVector[0] + lineVector[1]*lineVector[1])
	lineVector[0] = lineVector[0] / lineLength
	lineVector[1] = lineVector[1] / lineLength

	# rotacija vektora za 90 stupnjeva
	temp = lineVector[0]
	lineVector[0] = -lineVector[1]
	lineVector[1] = temp

	# tocka na liniji okomita na corner3
	#lineDotX = (int)(corner3X + lineVector[0] * corner3DistanceToLine)
	#lineDotY = (int)(corner3Y + lineVector[1] * corner3DistanceToLine)

	calculatedCorner3X = (int)(corner1X + rectangleOrientation * lineVector[0] * corner3DistanceToLine)
	calculatedCorner3Y = (int)(corner1Y + rectangleOrientation * lineVector[1] * corner3DistanceToLine)

	calculatedCorner4X = (int)(corner2X + rectangleOrientation * lineVector[0] * corner3DistanceToLine)
	calculatedCorner4Y = (int)(corner2Y + rectangleOrientation * lineVector[1] * corner3DistanceToLine)

# dobivanje koordinata sredisnjeg kvadrata
def getWindowCenterSquareCoordinates(image):
	generalXLow = (int)(((image.shape[1]-1) / 2) - constants.centerSquareSideLength)
	generalYLow = (int)(((image.shape[0]-1) / 2) - constants.centerSquareSideLength)
	generalXHigh = (int)(((image.shape[1]-1) / 2) + constants.centerSquareSideLength)
	generalYHigh = (int)(((image.shape[0]-1) / 2) + constants.centerSquareSideLength)

	return generalXLow, generalYLow, generalXHigh, generalYHigh

# provjera ako je mjerni marker unutar granica sredisnjeg kvadrata
def checkMeasuringMarkerPosition(image, centerX, centerY):
	generalXLow, generalYLow, generalXHigh, generalYHigh = getWindowCenterSquareCoordinates(image)
	if centerX > generalXLow and centerX < generalXHigh and centerY > generalYLow and centerY < generalYHigh:
		return True

# izracun udaljenosti izmedu 2 tocke
def distanceBetweenTwoPoints(p0, p1):
	return (int)(math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2))

# PRIKAZ I CRTANJE
# ----------------------------------------------------------------------------------------------------------------------------
# prikaz prozora
def refreshWindows(image, focusedTrackImage):
	cv2.imshow('Focused track', focusedTrackImage)
	cv2.imshow('Gate setup', image)
	#cv2.imshow('Rotated gate setup', rotated)

	if cv2.waitKey(3) & 0xFF == ord('q'):
		return False
	return True

# crtanje pojedinacnog markera
def drawMarker(image, markerID, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY):
	#cv2.line(image, topLeft, topRight, constants.green, constants.lineWidth)
	#cv2.line(image, topRight, bottomRight, constants.green, constants.lineWidth)
	#cv2.line(image, bottomRight, bottomLeft, constants.green, constants.lineWidth)
	#cv2.line(image, bottomLeft, topLeft, constants.green, constants.lineWidth)

	#if markerID == constants.corner1ID or markerID == constants.corner2ID or markerID == constants.corner3ID:
	#	cv2.circle(image, (centerX, centerY), constants.circleRadius, constants.red, constants.circleWidth)
	#else:
	
	cv2.circle(image, (centerX, centerY), constants.circleRadius, constants.red, constants.circleWidth)

# crtanje fokusirane staze
def drawFoucusedTrackWindow(image, focusedTrackImage, ids, markerID, centerX, centerY):
	# ako nisu svi markeri pronadeni izlazi i vraca primljenu sliku (zadnju u nizu)
	if constants.corner1ID not in ids and constants.corner2ID not in ids and constants.corner3ID not in ids: return focusedTrackImage

	# get corners and focused track coordinates
	setTrackCorners(markerID, centerX, centerY)
	# get4thCorer(image)
	(minCornerX, minCornerY, maxCornerX, maxCornerY) = getFocusedTrackCoordinates(image.shape[1]-1, image.shape[0]-1)

	# visual representation of the boundaries
	drawTrackBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY)

	# alter focused track image dimensions
	if 0 not in {minCornerX, minCornerY, maxCornerX, maxCornerY}:
		focusedTrackImage = image[minCornerY+constants.circleRadius:maxCornerY-constants.circleRadius, minCornerX+constants.circleRadius:maxCornerX-constants.circleRadius]

	return focusedTrackImage

# crtanje granica
def drawTrackBoundaries(image, minCornerX, minCornerY, maxCornerX, maxCornerY):
	calculateImaginaryBoundaries()

	# tocke krajnjih granica staze
	cv2.circle(image, (minCornerX, minCornerY), constants.circleRadius, constants.yellow, constants.circleWidth)
	cv2.circle(image, (maxCornerX, maxCornerY), constants.circleRadius, constants.yellow, constants.circleWidth)

	# slucaj kada marker za sirinu nije na ekranu
	if (corner2X == 0 and corner2Y == 0) or (corner3X == 0 and corner3Y == 0): return 

	# prikaz linija
	# 0-1
	cv2.line(image, (corner1X, corner1Y), (corner2X, corner2Y), constants.blue, constants.lineWidth)

	# pravokutnik izracunatih granica
	cv2.line(image, (calculatedCorner3X, calculatedCorner3Y), (corner1X, corner1Y), constants.blue, constants.lineWidth)
	cv2.line(image, (calculatedCorner4X, calculatedCorner4Y), (corner2X, corner2Y), constants.blue, constants.lineWidth)
	cv2.line(image, (calculatedCorner3X, calculatedCorner3Y), (calculatedCorner4X, calculatedCorner4Y), constants.blue, constants.lineWidth)

# crtanje orijentacija markera
def drawMarkerOrientations(image, rotationVector, translationVector):
	index = -1
	for x in rotationVector:
		index += 1
		rotVector = rotationVector[index]
		transVector = translationVector[index]
		cv2.aruco.drawAxis(image, cameraMatrix, cameraDistortionCoefficients, rotVector, transVector, constants.markerOrientationLength)

# crtanje sredisnjeg kvadrata
def drawCenterMeasuringSquare(image):
	generalXLow, generalYLow, generalXHigh, generalYHigh = getWindowCenterSquareCoordinates(image)
	cv2.rectangle(image ,(generalXLow, generalYLow),(generalXHigh, generalYHigh), constants.red, constants.lineWidth)


# main program
# ----------------------------------------------------------------------------------------------------------------------------
def mainLoop(pipeline):
	global rotated

	# lokalne varijable
	calibrationMarkerDiagonalPixels = 0 	# broj piksela u dijagonali markera koji oznacuje pocetno stanje, koristen za odredivanje udaljenosti
	pixelToMeterRatio = 0 					# omjer piksela i udaljenosti na slici
	looping = True 							# ako je fasle se program prestaje izvrsavati
	measuringMarkerInsideLimits = False		# provjera ako je 0-ti marker unutar granica
	distanceSet = False						# provjera ako je relativna udaljenost odredena

	# inicijalizacija razlicitih frameova (okvira) koji se koriste
	focusedTrackImage = pipelineToImage(pipeline)	# granice staze, bez okolnih stvari
	rotated = pipelineToImage(pipeline)				# prikazana staza u ravnini sa prozorom

	# petlja
	while looping:
		image = pipelineToImage(pipeline)	# pretvorba frameova u sliku

		corners, ids, rotationVector, translationVector = findArucoMarkers(image) 	# nalazenje markera na slici

		# crtanje granica u kojima treba biti mjerni marker
		if not measuringMarkerInsideLimits: drawCenterMeasuringSquare(image)

		# ako nije pronasao niti jedan marker, vraca se na pocetak petlje
		if not len(corners):
			looping = refreshWindows(image, focusedTrackImage)
			continue

		ids = ids.flatten()		# ([[1,2], [3,4]]) -> ([1, 2, 3, 4])

		# prolazak kroz sve markere
		for (markerCorner, markerID) in zip(corners, ids):
			if markerID != constants.measuringMarkerID and not measuringMarkerInsideLimits: continue # prolazak po markerima dok se ne pronade mjerni marker, ali samo ako nije unutar granica
			corners = markerCorner.reshape((4, 2)) #promjena matrice u dimenzije 4 para
			topLeft, topRight, bottomRight, bottomLeft, centerX, centerY = getMarkerCoordinates(corners) 	# koordinate svih tocaka markera
			drawMarker(image, markerID, topLeft, topRight, bottomRight, bottomLeft, centerX, centerY)	# crtanje obruba i centra markera

			# provjera ako je mjerni marker unutar kalibracijskih granica
			if not measuringMarkerInsideLimits:
				measuringMarkerInsideLimits = checkMeasuringMarkerPosition(image, centerX, centerY)
				# ako nakon provjere nije, proces krece ispocetka
				if not measuringMarkerInsideLimits: break

			# odredivanje udaljenosti kada je mjerni marker unutar granica, ali udaljenost nije odredena
			if not distanceSet and markerID == constants.measuringMarkerID:
				calibrationMarkerDiagonalPixels = distanceBetweenTwoPoints(topLeft, bottomRight)
				constants.borderCircleRadius = (int)(3 * calibrationMarkerDiagonalPixels / 4)
				pixelToMeterRatio = calibrationMarkerDiagonalPixels / constants.markerDiagonalLength
				distanceSet = True
			
			# pocetak programa nakon kalibracije udaljenosti
			# pronalazenje i crtanje vanjskih granica
			focusedTrackImage = drawFoucusedTrackWindow(image, focusedTrackImage, ids, markerID, centerX, centerY)

		# crtanje vektora orijentacije markera
		#drawMarkerOrientations(image, rotationVector, translationVector)

		# prikaz glavnih prozora
		looping = refreshWindows(image, focusedTrackImage)	

def main():
	# D435i setup i kalibracija
	global cameraMatrix
	global cameraDistortionCoefficients
	pipeline = pipelineInitilazation()
	cameraMatrix, cameraDistortionCoefficients = pipelineCalibration(pipeline)

	# glavna petlja
	mainLoop(pipeline)

	# prestanak primanja podataka od kamera
	pipeline.stop()

if __name__ == "__main__": 
	main()