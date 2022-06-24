INPUT=$1
#0-1 where 1 means lossless
QUALITY=$2
FRAME_SIZE=1920

#https://github.com/libjxl/libjxl
CJLX=cjlx
FFMPEG=ffmpeg
ZIPPER=7z
CONVERTER="./anythingToImage.py"

WORKING_DIR="./working"
COMPRESSED_DIR=$WORKING_DIR"/compressed"
DECOMPRESSED_DIR=$WORKING_DIR"/decompressed"
mkdir -p $WORKING_DIR
mkdir -p $COMPRESSED_DIR
mkdir -p $DECOMPRESSED_DIR

MODES=("gray" "rgb")

IN_EXTENSION="${INPUT##*.}"

#Convert to image

for MODE in "${MODES[@]}"; do
    FILE=$WORKING_DIR"/"$MODE".png"
    python $CONVERTER $INPUT $FILE $MODE 8
    python $CONVERTER $FILE $DECOMPRESSED_DIR"/"$MODE""$IN_EXTENSION

    QUALITY_JP=$(bc -l <<< $QUALITY*100)
    QUALITY_JP=${QUALITY_JP%.*}
    FILE_JP=$COMPRESSED_DIR"/"$MODE".jxl"
    $CJLX $OUT_FILE $WORKING_DIR"/"$OUT_FILE $FILE_JP --modular --quality QUALITY_JP --speed 9 -E 3
    python $CONVERTER $FILE_JP $DECOMPRESSED_DIR"/jp"$MODE"."$IN_EXTENSION
 
    FRAMES_DIR=$WORKING_DIR"/frames"$MODE
    mkdir -p $FRAMES_DIR
    python $CONVERTER $INPUT $FRAMES_DIR"/.png" 8 $FRAME_SIZE
    QUALITY_AV=$(bc -l <<< (1.0-$QUALITY)*63)
    QUALITY_AV=${QUALITY_AV%.*}
    VIDEO_FILE=$COMPRESSED_DIR"/"$MODE".mkv"
    $FFMPEG -i $FRAMES_DIR"/%05d.png" -c:v libaom-av1 -crf $QUALITY_AV -b:v 0 $VIDEO_FILE 
    DECOMPRESSED_FRAMES_DIR=$DECOMPRESSED_DIR"/frames"$MODE
    mkdir -p $DECOMPRESSED_FRAMES_DIR
    $FFMPEG -i $VIDEO_FILE $DECOMPRESSED_FRAMES_DIR"/%05d.png"
    python $CONVERTER $DECOMPRESSED_FRAMES_DIR $DECOMPRESSED_DIR"/frames"$MODE"."$IN_EXTENSION
done

ZIPPED_FILE=$COMPRESSED_DIR"/zipped.7z"
$ZIPPER a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on $ZIPPED_FILE $INPUT
$ZIPPER e -y $ZIPPED_FILE -o $DECOMPRESSED_DIR"/7z."$IN_EXTENSION 

#Print sizes

ORIGINAL_SIZE=$(stat -c%s "$INPUT")
echo "Original size: "$ORIGINAL_SIZE
ZIPPED_SIZE=$(stat -c%s "$ZIPPED_FILE")
ZIPPED_SIZE_P=$(bc -l <<< ($ZIPPED_SIZE/$ORIGINAL_SIZE)*100)
echo "Zipped size: "$ZIPPED_SIZE "("$ZIPPED_SIZE_P")%"
for MODE in "${MODES[@]}"; do
    SIZE=$(stat -c%s "$WORKING_DIR/$MODE.png")
    SIZE_P=$(bc -l <<< ($SIZE/$ORIGINAL_SIZE)*100)
    echo $MODE" PNG size: "$SIZE "("$SIZE_P")%"

    SIZE=$(stat -c%s "$COMPRESSED_DIR/$MODE.jxl")
    SIZE_P=$(bc -l <<< ($SIZE/$ORIGINAL_SIZE)*100)
    echo $MODE" JPG size: "$SIZE "("$SIZE_P")%"
    
    FRAMES_DIR=$WORKING_DIR"/frames"$MODE
    SIZE=$(du -hsb $FRAMES_DIR | cut -f -1)
    SIZE_P=$(bc -l <<< ($SIZE/$ORIGINAL_SIZE)*100)
    echo $MODE" PNG frames size: "$SIZE "("$SIZE_P")%"
    
    SIZE=$(stat-c%s $COMPRESSED_DIR/$MODE".mkv")
    SIZE_P=$(bc -l <<< ($SIZE/$ORIGINAL_SIZE)*100)
    echo $MODE" AV1 frames size: "$SIZE "("$SIZE_P")%"
done

#Reference compression methods

function textCompression
{
    RESULT=$WORKING_DIR"/reference.zip"
    zip -9  $INPUT $RESULT
    return $RESULT
}

#Quality measurements methods

function textDiff
{
    RESULT=$(wdiff $INPUT $1)
    RESULT=($RESULT)
    return ${RESULT[-2]}
}

REF_COMPRESSED=textCompression()
SIZE=$(stat-c%s $REF_COMPRESSED)
SIZE_P=$(bc -l <<< ($SIZE/$ORIGINAL_SIZE)*100)
echo $MODE" Reference compression size: "$SIZE "("$SIZE_P")%"

#Evaluate quality
FILES=($(ls $1))
for F in "${FILES[@]}"; do
    echo $F" "$(textDiff)
done

