import numpy as np
import pytesseract
import cv2
from PIL import Image

def getWord(roi):
    roiBW = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, roiThresh = cv2.threshold(roiBW, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    Image.fromarray(roiThresh).save('croppedImg.jpg')

    # config = "-l eng --oem 1 --psm 8"
    text = pytesseract.image_to_string('croppedImg.jpg', lang='eng')
    if not text:
        _, roiThresh = cv2.threshold(roiBW, 111, 255, cv2.THRESH_BINARY)
        Image.fromarray(roiThresh).save('croppedImg.jpg')
        text = pytesseract.image_to_string('croppedImg.jpg', lang='eng')
        if not text:
            return ''

    text = max(text.split('\n'), key=lambda line: len(line))

    from string import ascii_letters
    tmp = text
    text = ''
    for letter in tmp:
        if letter in ascii_letters + ' ':
            text += letter
    text = text.strip()
    return text

def getBoxes(unmodifiedImg):
    print('avg pixel:', np.average(np.average(unmodifiedImg, axis=0), axis=0))

    int16Img = unmodifiedImg.astype('int16')
    # necessary to avoid overflow or something
    redBlueDiff = (int16Img[:, :, 0] - int16Img[:, :, 2])

    # get the fourth-percentile of red-blue differences, approximately what a "white" pixel would have
    notBlack = np.sum(unmodifiedImg, axis=2) > 150
    flattenedDiffNoBlack = np.extract(notBlack, redBlueDiff)
    flattenedDiffNoBlack.sort()
    # percentile = 0.04 if len(flattenedDiffNoBlack) > resizeH*resizeW/2 else 0.15
    percentile = 0.04
    targetDiff = flattenedDiffNoBlack[int(len(flattenedDiffNoBlack) * percentile)] + 14
    print('threshold', targetDiff)

    ret, boxImg = cv2.threshold(redBlueDiff, targetDiff, 255, cv2.THRESH_BINARY)
    boxImg = boxImg.astype('uint8')
    Image.fromarray(boxImg).show()

    _, contours, _ = cv2.findContours(boxImg.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    imgWithContours = cv2.drawContours(unmodifiedImg.copy(), contours, -1, (255, 0, 0), 10)
    Image.fromarray(imgWithContours).show()

    imgWithTiltedRects = unmodifiedImg.copy()
    boundingRects = []

    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        _, (w, h), _ = rect
        h, w = sorted([w, h])  # make sure they're actually referring to the correct thing lmao
        # x, y, w, h = cv2.boundingRect(cnt)
        if 30 < h < 150 and 200 < w < 500:
            imgWithTiltedRects = cv2.drawContours(imgWithTiltedRects, [box], 0, (0, 0, 255), 10)
            rect = cv2.boundingRect(cnt)
            if getWord(rect, unmodifiedImg):
                boundingRects.append(rect)

    imgWithAlignedRects = unmodifiedImg.copy()
    for rect in boundingRects:
        x, y, w, h = rect
        imgWithAlignedRects = cv2.rectangle(imgWithAlignedRects, (x, y), (x + w, y + h), (0, 255, 0), 10)
    Image.fromarray(imgWithAlignedRects).show()

    boundingRects.sort(key=lambda xywh: xywh[1])
    gridOfRects = [boundingRects[i : i + 5] for i in range(0, 25, 5)]
    print(gridOfRects)
    for row in gridOfRects:
        row.sort(key=lambda xywh: xywh[0])
    boundingRects = []
    for row in gridOfRects:
        boundingRects += row
    wordList = list(map(lambda box: getWordFUNCTIONCHANGED(box, unmodifiedImg), boundingRects))
    print(wordList)

    print('numOfBoundingRects', len(boundingRects))
    Image.fromarray(imgWithTiltedRects).show()

def isolateCards(imageArr):
    # imageBlur = cv2.bilateralFilter(imageArr, 20, 30, 3)
    imageBlur = cv2.blur(imageArr, (30, 4))

    imageBW = cv2.cvtColor(imageBlur, cv2.COLOR_RGB2GRAY)
    imageThresh = cv2.adaptiveThreshold(imageBW, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                              cv2.THRESH_BINARY_INV, 201, -8)
    _, contours, _ = cv2.findContours(imageThresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    imgWithRects = imageArr.copy()
    rectList = []

    for cnt in contours:
        rect = cv2.boundingRect(cnt)
        x, y, w, h = rect
        if 120 < h < 400 and 240 < w < 600 and 1 < w/h < 3:
            rectList.append(rect)
    rectList.sort(key=lambda xywh: xywh[3], reverse=True)
    rectList = rectList[:25]

    for x, y, w, h in rectList:
        cv2.rectangle(imgWithRects, (x, y), (x + w, y + h), (0, 255, 0), 10)

    # Image.fromarray(imgArr).show()
    # Image.fromarray(imageBlur).show()
    # Image.fromarray(imageThresh).show()
    # imgWithContours = cv2.drawContours(imageArr.copy(), contours, -1, (255, 0, 0), 10)
    # Image.fromarray(imgWithContours).show()
    # Image.fromarray(imgWithRects).show()
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

if __name__ == '__main__':
    for i in range(1, 15):
        import time
        t0 = time.time()
        filename = 'testImages/example' + str(i) + '.jpg'
        print('TEST IMAGE', i)

        basewidth = 2560
        doNotUseThisImg = Image.open(filename)
        wpercent = (basewidth / float(doNotUseThisImg.size[0]))
        hsize = int((float(doNotUseThisImg.size[1]) * float(wpercent)))
        imgArr = np.array(doNotUseThisImg.resize((basewidth, hsize), Image.ANTIALIAS))

        borderSize = 30
        imgArr = cv2.copyMakeBorder(imgArr, borderSize, borderSize, borderSize, borderSize, cv2.BORDER_REPLICATE)

        rectangles = sortRects(isolateCards(imgArr))
        wordSnippets = map(lambda rect: extractWordFromCard(rect, imgArr), rectangles)
        wordList = list(map(getWord, wordSnippets))
        for i in range(5):
            print(wordList[5*i:5*i+5])
        print(time.time() - t0)



        # imageArr = np.array(Image.open(filename).resize((2000, 2400), Image.ANTIALIAS))
        # imageArr[np.where((imageArr < [120, 100, 100]).any(axis=2))] = [160, 140, 110]
        #
        # image = Image.fromarray(imageArr)
        # contrast = ImageEnhance.Contrast(image)
        # # contrast.enhance(3).show()
        # # image.show()
        # Image.open(filename).show()
        # ImageEnhance.Sharpness(Image.open(filename)).enhance(10).show()
