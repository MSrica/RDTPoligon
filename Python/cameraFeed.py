"""
Links
QR code 
	- https://towardsdatascience.com/build-your-own-barcode-and-qrcode-scanner-using-python-8b46971e719e
	- https://pypi.org/project/pyzbar/
CV2 video - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
OPENCV - https://opencv-python-tutroals.readthedocs.io/en/latest/index.html
"""

# libraries
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol

camera_port = 0
camera = cv2.VideoCapture(camera_port, cv2.CAP_DSHOW)

"""
This function takes an image, then identifies the QRcode from the image, and decodes the value of it. 
Here barcode is a list of barcode and QRcode objects recognized by the decode function. 
Each object contains rect, polygon, data, type, etc attributes. 
rect and polygon attributes give the position of barcode and QRcode
"""
def QRDecoder(image):
	grayImage = cv2.cvtColor(image, 0)
	barcode = decode(grayImage, symbols = [ZBarSymbol.QRCODE])

	for obj in barcode:
		points = obj.polygon
		pts = np.array(points, np.int32)
		pts = pts.reshape((-1, 1, 2))
		xLowerLeft = pts[0][0][0]
		yLowerLeft = pts[0][0][1]
		xUpperLeft = pts[1][0][0]
		yUpperLeft = pts[1][0][1]
		xUpperRight = pts[2][0][0]
		yUpperRight = pts[2][0][1]
		xLowerRight = pts[3][0][0]
		yLowerRight = pts[3][0][1]
		cv2.polylines(image, [pts], True, (100, 255, 0), 2)

		barcodeData = obj.data.decode("utf-8")
		string = "Data: " + str(barcodeData)

		cv2.putText(image, "1", (xLowerLeft, yLowerLeft), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255), 2)
		cv2.putText(image, "2", (xUpperLeft, yUpperLeft), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255), 2)
		cv2.putText(image, "3", (xUpperRight, yUpperRight), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255), 2)
		cv2.putText(image, "4", (xLowerRight, yLowerRight), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255), 2)


def main():
	while True:
		# Capture frame-by-frame
		ret, frame = camera.read()

		QRDecoder(frame)

		# Display the resulting frame
		cv2.imshow('image', frame)
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break

if __name__ == "__main__":
	main()

# When everything done, release the camera
camera.release()
cv2.destroyAllWindows()