#arguments: inputFile, outputFile

import math
import sys
import os
import cv2
import numpy

file = open(sys.argv[1], "rb")
size = os.stat(sys.argv[1]).st_size
dimension = math.ceil(math.sqrt(size/3))
result = numpy.zeros(dimension*dimension*3, numpy.uint8)

byte = file.read(1)
i=0
while byte:
    result[i] = int.from_bytes(byte, "big")
    byte = file.read(1)
    i += 1

for j in range(i,size):
    result[j] = 0

result = numpy.reshape(result, (dimension, dimension, 3))
cv2.imwrite(sys.argv[2], result)
