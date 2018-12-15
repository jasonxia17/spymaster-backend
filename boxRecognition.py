import numpy as np
import pytesseract
import cv2
from PIL import Image
from autocorrect import spell

def getWord(roi):
    roiBW = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, roiThresh = cv2.threshold(roiBW, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(roiThresh, lang='eng')

    if not text: # second try using different threshold
        _, roiThresh = cv2.threshold(roiBW, 128, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(roiThresh, lang='eng')
        print('SUCCESS ON 2ND TRY FOR:', text)
        if not text:
            print('BIG FAIL POOPOO')
            return 'COULD NOT PARSE'

    if text != spell(text):
        print('AUTOCORRECT REQUIRED ON', text)

    return spell(text)

def insideOfRect(rectIn, rectOut):
    xi, yi, wi, hi = rectIn
    xo, yo, wo, ho = rectOut

    return xi > xo and yi > yo and xi + wi < xo + wo and yi + hi < yo + ho

def isAnOuterRect(rect, rectList):
    for rect2 in rectList:
        if insideOfRect(rect, rect2):
            return False
    return True

def removeOutlierRects(rectList):
    maxDeviation = [320, 200]
    for xOrY in (0, 1):
        for reverse in (False, True):
            rectList.sort(key=lambda rect: rect[xOrY], reverse=reverse)
            while abs(rectList[0][xOrY] - rectList[3][xOrY]) > maxDeviation[xOrY]:
                rectList.pop(0)
    return rectList

def isolateCards(imageArr):
    imageBW = cv2.cvtColor(imageArr, cv2.COLOR_RGB2GRAY)
    print('TOP-LEFT BRIGHTNESS', imageBW[0][0])

    bias = 3 if imageBW[0][0] > 140 else -8
    # Subtracting higher bias --> more dark areas; this is needed in a brighter image
    imageThresh = cv2.adaptiveThreshold(imageBW, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, 201, bias)
    if imageBW[0][0] > 140:
        # imageThresh = cv2.erode(imageThresh, np.ones((5, 5), np.uint8), iterations=3)
        # cuz you gotta deal with hardwood floors and other poop like that
        # could also use morphologyEx (erosion followed by dilation, but seems like erode works better)
        imageThresh = cv2.morphologyEx(imageThresh, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8), iterations=3)

    _, contours, _ = cv2.findContours(imageThresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rectList = []

    for cnt in contours:
        rect = cv2.boundingRect(cnt)
        x, y, w, h = rect
        if 120 < h < 400 and 240 < w < 600 and 1 < w/h < 3:
            rectList.append(rect)

    rectList = list(filter(lambda rect: isAnOuterRect(rect, rectList), rectList))

    rectList = removeOutlierRects(rectList)

    imgWithRects = imageArr.copy()
    for x, y, w, h in rectList:
        cv2.rectangle(imgWithRects, (x, y), (x + w, y + h), (0, 255, 0), 30)

    # Image.fromarray(imageArr).show()
    # Image.fromarray(imageBW).show()
    # Image.fromarray(imageThresh).show()
    # imgWithContours = cv2.drawContours(imageArr.copy(), contours, -1, (255, 0, 0), 10)
    # Image.fromarray(imgWithContours).show()
    # Image.fromarray(imgWithRects).show()

    if len(rectList) != 25:
        print("UH OH, something went wrong")
        Image.fromarray(imgWithRects).show()

    return rectList

def sortRects(boundingRects):
    boundingRects.sort(key=lambda xywh: xywh[1])
    gridOfRects = [boundingRects[i: i + 5] for i in range(0, 25, 5)]
    for row in gridOfRects:
        row.sort(key=lambda xywh: xywh[0])
    boundingRects = []
    for row in gridOfRects:
        boundingRects += row
    return boundingRects

def extractWordFromCard(box, unmodifiedImg):
    x, y, w, h = box
    roi = unmodifiedImg[y: y + h, x: x + w]
    roi = cv2.resize(roi, (300, 200), interpolation=cv2.INTER_CUBIC)
    roi = roi[115:165, 50:250]
    return roi.copy()

def imageToWordList(filename):
    basewidth = 2560
    doNotUseThisImg = Image.open(filename)
    wpercent = (basewidth / float(doNotUseThisImg.size[0]))
    hsize = int((float(doNotUseThisImg.size[1]) * float(wpercent)))
    imgArr = np.array(doNotUseThisImg.resize((basewidth, hsize), Image.ANTIALIAS))

    borderSize = 30
    imgArr = cv2.copyMakeBorder(imgArr, borderSize, borderSize, borderSize, borderSize,
                                cv2.BORDER_REPLICATE)
    rectangles = sortRects(isolateCards(imgArr))

    wordSnippets = map(lambda rect: extractWordFromCard(rect, imgArr), rectangles)
    wordList = list(map(getWord, wordSnippets))
    for i in range(5):
        print(wordList[5 * i:5 * i + 5])
    return wordList

if __name__ == '__main__':
    for i in range(14, 15):
        filename = 'testImages/example' + str(i) + '.jpg'
        print('TEST IMAGE', i)
        imageToWordList(filename)
        print()

