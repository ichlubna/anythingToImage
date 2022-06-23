# Any file to image convertor
The script read the input file in a binary mode and saves the bytes in an image file.

Tested with 8 and 16bit PNG files. Other formats might be problematic due to lossy compression or unsupported bit depths.

Examples:
```
python anythingToImage inputFile output.png rgb|gray 8|16
python anythingToImage inputImage.png outputFile
```

Can produce multiple images limited by resolution:
```
python anythingToImage inputFile output.png rgb|gray 8|16 maxResolution
python anythingToImage inputFolder outputFile
```
