import math
import sys
import os
import cv2
import numpy
from PIL import Image

def toImage():
    file = open(sys.argv[1], "rb")
    size = os.stat(sys.argv[1]).st_size
    depth = 3
    if sys.argv[3] == "gray":
        depth = 1
    dimension = math.ceil(math.sqrt(size/depth))
    result = numpy.zeros(dimension*dimension*depth, numpy.uint8)
    reads = 1
    if sys.argv[4] == "16":
        dimension = math.ceil(math.sqrt(math.ceil(size/2)/depth))
        result = numpy.zeros(dimension*dimension*depth, numpy.uint16)
        reads = 2

    byte = file.read(1)
    i = 0
    while byte:
        byteList = [0,0]
        for j in range(reads):
            byteList[j] = int.from_bytes(byte, "little")
            byte = file.read(1)
        result[i] = int.from_bytes(byteList, "little")
        #print(chr(result[i]))
        i += 1

    result = numpy.reshape(result, (dimension, dimension, depth))
    cv2.imwrite(sys.argv[2], result)

def fromImage():
    im = Image.open(sys.argv[1])
    mode = cv2.IMREAD_GRAYSCALE
    depth = 1
    if im.mode == "RGB":
        mode = cv2.IMREAD_COLOR
        depth = 3
    img = cv2.imread(sys.argv[1], mode)
    height = img.shape[0]
    width = img.shape[1]
    data = [0] * width*height*depth
    l = 0
    for i in range(0, height):
         for j in range(0, (width)):
            if im.mode == "RGB":
                for k in range(0,depth):
                   data[l] = img[i,j,k]
                   l += 1
            else:
               data[l] = img[i,j]
               l += 1
    file = open(sys.argv[2], "wb")
    fileByteArray = bytearray(data)
    file.write(fileByteArray)

if sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("Arguments: inputFile, outputFile, mode: gray|rgb, bit 8|16 \nIf only first two arguments are used, the reverse image to file conversion is performed")

if len(sys.argv) > 3:
    toImage()
else:
    fromImage()
