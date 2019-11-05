import cv2
import sys
import numpy
import numpy as np
import imutils

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit ,
    QGridLayout
)


class Example(QWidget):
    def canny_layout(self):
        canny = QGridLayout()
        canny.addWidget(QLabel("Canny threshold"), 1,0)
        canny_1 = QLineEdit()        
        canny_1_label = QLabel("1")        
        canny_1.setText(f"{self.canny_1}")
        canny_1.textChanged.connect(self.set_canny_1)

        canny_2_label = QLabel("2")
        canny_2 = QLineEdit()        
        canny_2.setText(f"{self.canny_2}")
        canny_2.textChanged.connect(self.set_canny_2)


        canny_3 = QLineEdit()        
        canny_3.setText(f"{self.canny_3}")
        canny_3.textChanged.connect(self.set_canny_2)

        canny.addWidget(canny_1_label, 3,0)
        canny.addWidget(canny_1,3,1)
        canny.addWidget(canny_2_label, 4,0)
        canny.addWidget(canny_2,4,1)
        canny.addWidget(QLabel("3"), 5,0)
        canny.addWidget(canny_3,5,1)

        return canny

    def rotate_layout(self):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("Rotate"), 0,0)
        canny_1 = QLineEdit() 
        canny_1.setText(f"{self.rotate_deg}")
        canny_1_label = QLabel("deg")        
        canny_1.textChanged.connect(self.set_rotate)

        layout.addWidget(canny_1_label, 3,0)
        layout.addWidget(canny_1,3,1)
        layout.addWidget(canny_1,4,1)

        return layout 

    def gaussian_blur_layout(self):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("GaussianBlur"), 0,0)

        _1 = QLineEdit() 
        _1_label = QLabel("ksize width")        
        _1.textChanged.connect(self.set_ksize_width)

        _2 = QLineEdit() 
        _2_label = QLabel("ksize height")        
        _2.textChanged.connect(self.set_ksize_height)

        layout.addWidget(_1_label, 2,0)
        layout.addWidget(_1,2,1)
        layout.addWidget(_2_label, 3,0)
        layout.addWidget(_2,3,1)

        return layout 

    def contours_layout(self):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("Contour"), 0,0)

        canny_1_label = QLabel("draw")        
        canny_1 = QCheckBox() 
        canny_1.toggled.connect(lambda:self.contours_state(canny_1))

        layout.addWidget(canny_1_label, 3,0)
        layout.addWidget(canny_1,3,1)
        layout.addWidget(canny_1,4,1)

        return layout

    def __init__(self):
        super().__init__()
        self.image_data = None
        self.image = None
        self.canny_1 = 20
        self.canny_2 = 200 
        self.canny_3 = 255 
        self.ksize_height = 5
        self.ksize_width = 5
        self.rotate_deg = 0 
        self.contours = False
        self.label = QLabel()
        self.initUI()

        with open("./images/CAPTURE.png", "rb") as file:
            self.data = numpy.array(bytearray(file.read()))
            self.image = cv2.imdecode(self.data, cv2.IMREAD_UNCHANGED)

            self.showImage()

    def initUI(self):
        self.label.setText("OpenCV Image")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: gray; border-style:solid; border-width: 1px;")

        btn_open = QPushButton("Open image...")
        btn_open.clicked.connect(self.open_image)

        btn_process = QPushButton("Proces image")
        btn_process.clicked.connect(self.process_image)

        btn_reset = QPushButton("Reset image")
        btn_reset.clicked.connect(self.reset)

        top_bar = QGridLayout()
        top_bar.addWidget(btn_open, 1,0)
        top_bar.addWidget(btn_process, 1, 1)
        top_bar.addWidget(btn_reset, 1, 2)

        settings = QGridLayout()
        settings.setAlignment(Qt.AlignTop)
        settings.addLayout(self.rotate_layout(), 1, 0)
        settings.addLayout(self.canny_layout(), 1, 1)
        settings.addLayout(self.gaussian_blur_layout(), 1, 2)
        settings.addLayout(self.contours_layout(), 2, 0)


        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignTop)
        root.addLayout(top_bar)
        root.addLayout(settings)
        root.addWidget(self.label)

        self.resize(540, 574)
        self.setWindowTitle("OpenCV & PyQT 5 example")

    def reset(self):
        self.image = cv2.imdecode(self.data, cv2.IMREAD_UNCHANGED)
        self.showImage()

    def contours_state(self, item):
        self.contours = item.isChecked()
        self.process_image()

    def set_ksize_width(self, value):
        try:
            self.ksize_width = int(value)
        except ValueError: 
            self.ksize_width = 0  
        self.process_image()

    def set_ksize_height(self, value):
        try:
            self.ksize_height = int(value)
        except ValueError: 
            self.ksize_height = 0  
        self.process_image()

    def set_canny_1(self, value):
        try:
            self.canny_1 = int(value)
        except ValueError: 
            self.canny_1 = 0  
        self.process_image()

    def set_canny_2(self, value):
        try:
            self.canny_2 = int(value)
        except ValueError: 
            self.canny_2 = 0  
        self.process_image()

    def set_canny_3(self, value):
        try:
            self.canny_3 = int(value)
        except ValueError: 
            self.canny_3 = 0  
        self.process_image()

    def set_rotate(self, value):
        try:
            self.rotate_deg = int(value)
        except ValueError: 
            self.rotate_deg = 0  
        self.process_image()

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, "File types", ".", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename:
            with open(filename, "rb") as file:
                self.data = numpy.array(bytearray(file.read()))
                self.image = cv2.imdecode(self.data, cv2.IMREAD_UNCHANGED)

                self.showImage()


    def order_points(self, pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    def four_point_transform(self, image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")

        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        # return the warped image
        return warped


    def process_image(self):
        self.image = cv2.imdecode(self.data, cv2.IMREAD_UNCHANGED)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) #convert to grey scale
        if (self.ksize_width > 0 and self.ksize_height > 0 and (self.ksize_height % 2) != 0 and (self.ksize_width % 2) != 0):
            self.image = cv2.GaussianBlur(self.image, (self.ksize_height, self.ksize_width), 0)

        if (self.rotate_deg != 0):
            self.image = imageutils.rotate_bound(self.image, self.rotate_deg) 

        if (self.canny_1 != 0 or self.canny_2 != 0 or self.canny_3 != 0):
            self.image = cv2.Canny(self.image, self.canny_1, self.canny_2, self.canny_3)

        if (self.contours):
            #contours, hierarchy = cv2.findContours(self.image,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
            #cv2.drawContours(self.image, contours, -1, (0, 255, 0), 3) 

            cnts = cv2.findContours(self.image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            displayCnt = None
            
            # loop over the contours
            for c in cnts:
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
                # if the contour has four vertices, then we have found
                # the thermostat display
                if len(approx) == 4:
                    displayCnt = approx
                    break

            self.image = self.four_point_transform(cv2.imdecode(self.data, cv2.IMREAD_UNCHANGED), displayCnt.reshape(4, 2))

        self.showImage()



    def showImage(self):
        size = self.image.shape
        step = self.image.size / size[0]
        qformat = QImage.Format_Indexed8

        if len(size) == 3:
            if size[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        img = QImage(self.image, size[1], size[0], step, qformat)
        img = img.rgbSwapped()

        self.label.setPixmap(QPixmap.fromImage(img))
        self.resize(self.label.pixmap().size())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Example()
    win.show()
    sys.exit(app.exec_())
