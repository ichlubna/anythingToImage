import math
import sys
import os
import cv2
import numpy
from PIL import Image

def toImage():
    path, fileName = os.path.split(sys.argv[2])

    dimension = -1
    if len(sys.argv) > 5:
        dimension = int(sys.argv[5])

    file = open(sys.argv[1], "rb")
    depth = 3
    if sys.argv[3] == "gray":
        depth = 1

    size = os.stat(sys.argv[1]).st_size
    if dimension == -1:
        dimension = math.ceil(math.sqrt(size/depth))
        if sys.argv[4] == "16":
            dimension = math.ceil(math.sqrt(math.ceil(size/2)/depth))
            size /= 2
    sizeLimit = dimension*dimension*depth

    fileCount = int(math.ceil(float(size)/sizeLimit))
    for b in range(0, fileCount):
        result = numpy.zeros(dimension*dimension*depth, numpy.uint8)
        reads = 1
        if sys.argv[4] == "16":
            result = numpy.zeros(dimension*dimension*depth, numpy.uint16)
            reads = 2

        for i in range(0, len(result)):
            result[i] = int.from_bytes(file.read(reads), "little")

        result = numpy.reshape(result, (dimension, dimension, depth))
        cv2.imwrite(os.path.join(path, str(b).zfill(5)+fileName), result)

def fromImage():
    path, fileName = os.path.split(sys.argv[1])
    files = [ fileName ]
    if os.path.isdir(sys.argv[1]):
        files = sorted(os.listdir(sys.argv[1]))
    im = Image.open(os.path.join(path,files[0]))
    mode = cv2.IMREAD_GRAYSCALE
    depth = 1
    if im.mode == "RGB":
        mode = cv2.IMREAD_COLOR
        depth = 3

    allData = []
    for inputFile in files:
        img = cv2.imread(os.path.join(path, inputFile), mode | cv2.IMREAD_ANYDEPTH)

        byteCount = 1
        if img.dtype == numpy.uint16:
            byteCount = 2

        height = img.shape[0]
        width = img.shape[1]
        data = [0] * width*height*depth*byteCount
        l = 0
        for i in range(0, height):
             for j in range(0, (width)):
                if im.mode == "RGB":
                    for k in range(0,depth):
                        for b in range(0,byteCount):
                            data[l] = (img[i,j,k] & (0xff << (b * 8))) >> (b * 8)
                            l += 1
                else:
                    for b in range(0,byteCount):
                        data[l] = (img[i,j] & (0xff << (b * 8))) >> (b * 8)
                        l += 1
        allData += data

    file = open(sys.argv[2], "wb")
    fileByteArray = bytearray(allData)
    file.write(fileByteArray)

if sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("Arguments: inputFile, outputFile, mode: gray|rgb, bit 8|16, image resolution (one dimension) \nIf only first two arguments are used, the reverse image to file conversion is performed \nThe input can also be folder in case of decoding")
    exit(0)

if len(sys.argv) > 3:
    toImage()
else:
    fromImage()
