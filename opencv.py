import cv2
import sys
import numpy
import numpy as np

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
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
        canny_1.textChanged.connect(self.set_canny_1)

        canny_2_label = QLabel("2")
        canny_2 = QLineEdit()        
        canny_2.textChanged.connect(self.set_canny_2)

        canny.addWidget(canny_1_label, 3,0)
        canny.addWidget(canny_1,3,1)
        canny.addWidget(canny_2_label, 4,0)
        canny.addWidget(canny_2,4,1)

        return canny

    def rotate_layout(self):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("Rotate"), 0,0)
        canny_1 = QLineEdit() 
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


    def __init__(self):
        super().__init__()
        self.image_data = None
        self.image = None
        self.canny_1 = 0 
        self.canny_2 = 0 
        self.ksize_height = 0 
        self.ksize_width = 0 
        self.rotate_deg = 0 
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

    def process_image(self):
        self.image = cv2.imdecode(self.data, cv2.IMREAD_UNCHANGED)
        if self.image is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) #convert to grey scale
            if (self.ksize_width > 0 and self.ksize_height > 0 and (self.ksize_height % 2) != 0 and (self.ksize_width % 2) != 0):
                self.image = cv2.GaussianBlur(self.image, (self.ksize_height, self.ksize_width), 0)

            if (self.canny_1 != 0 or self.canny_2 != 0):
                self.image = cv2.Canny(self.image, self.canny_1, self.canny_2)

            if (self.rotate_deg != 0):
                self.image = self.rotate_bound(self.image, self.rotate_deg) 
 
            # gray = (
            #    cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            #    if len(self.image.shape) >= 3
            #    else self.image
            # )

            # blur = cv2.GaussianBlur(gray, (21, 21), 0, 0)

            # self.image = cv2.divide(gray, blur, scale=256)
            self.showImage()


    def rotate_bound(self, image, angle):
        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)
    
        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
    
        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
    
        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY
    
        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (nW, nH))


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
