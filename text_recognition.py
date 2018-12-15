from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import cv2
from PIL import Image
# from gensim.models import KeyedVectors
# filename = 'GoogleNews-vectors-negative300.bin.gz'
# model = KeyedVectors.load_word2vec_format(filename, binary=True, limit=100000)
# wordSet = model.wv.vocab.keys()
# def check(word, wordSet):
#     flag = True
#     if word.lower() not in wordSet:
#         flag = False
#     s = word[0]
#     s += word[1:].lower()
#     if s in wordSet:
#         flag = True
#     for c in word:
#         if c.islower():
#             flag = False
#         if c.isdigit():
#             flag = False
#         if not flag:
#             break
#     return flag

def text_detection(file):

    def decode_predictions(scores, geometry):
        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []

        for y in range(0, numRows):

            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]

            for x in range(0, numCols):
                if scoresData[x] < 0.3:
                    continue

                (offsetX, offsetY) = (x * 4.0, y * 4.0)
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])
        return (rects, confidences)



    image = cv2.imread(file)
    orig = image.copy()
    (origH, origW) = image.shape[:2]


    (newW, newH) = (480, 480)
    rW = origW / float(newW)
    rH = origH / float(newH)


    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]


    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    net = cv2.dnn.readNet("frozen_east_text_detection.pb")


    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)


    (rects, confidences) = decode_predictions(scores, geometry)
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    results = []
    blackedOut = np.array(Image.open(file))
    Image.fromarray(blackedOut).show()
    for (startX, startY, endX, endY) in boxes:

        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)


        dX = int((endX - startX) * 0.1)
        dY = int((endY - startY) * 0.1)


        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(origW, endX + (dX * 2))
        endY = min(origH, endY + (dY * 2))

        roi = blackedOut[startY:endY, startX:endX]
        blackedOut[startY:endY, startX:endX] = np.array([255, 0 , 0 , 0])


        f = Image.open(file)
        f = f.convert("RGBA")
        pixdata = f.load()
        pixel1 = pixdata[startX,startY]
        item1, item2, item3, item4 = pixel1
        if (item4 > 250):
            config = ("-l eng --oem 1 --psm 7")
            text = pytesseract.image_to_string(roi, config=config)
            results.append(((startX, startY, endX, endY), text))

    Image.fromarray(blackedOut).show()

    results = sorted(results, key=lambda r: r[0][1])
    words = []
    word = {}
    count = 0
    x = []
    for ((startX, startY, endX, endY), text) in results:
        text = "".join([c if ord(c) < 123 else "" for c in text]).strip()
        if startX in word.keys():
            startX+=2
        word[startX] = text
        if count % 5 == 0:
            x.append([])
        x[int(count / 5)].append(startX)
        count+=1
    for i in range(0, len(x)):
        x[i].sort()
    for i in range(0, len(x)):
        words.append([])
        for j in range(0, len(x[i])):
            words[i].append(word[x[i][j]])
    return words
print(text_detection("testImages/example5.png"))