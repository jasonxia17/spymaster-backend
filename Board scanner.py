from text_recognition import text_detection
from gensim.models import KeyedVectors

file = "Codenames-Duet-Setup-2.jpg"
filename = 'GoogleNews-vectors-negative300.bin.gz'
model = KeyedVectors.load_word2vec_format(filename, binary = True, limit = 200000)
wordSet = model.wv.vocab.keys()

raw = text_detection(file)
board = []
for word in raw:
    if word.lower() not in wordSet:
        continue
    flag = True
    for c in word:
        if c.islower():
            flag = False
    if not flag:
        continue
    board.append(word)
print(board)