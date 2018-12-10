from gensim.models import KeyedVectors
from operator import itemgetter
filename = 'GoogleNews-vectors-negative300.bin.gz'
model = KeyedVectors.load_word2vec_format(filename, binary=True, limit=200000)

def getWordsHintedAt(clue, goodWords, badWords, neutralWords, assassins):
    # similar to scoring in curling
    # Append 0 to avoid bugs due to empty lists (i.e. no more neutral words)
    maxBadCloseness = max([model.similarity(clue, badWord) for badWord in badWords] + [0])
    maxNeutralCloseness = max([model.similarity(clue, word) for word in neutralWords] + [0])
    assassinCloseness = max([model.similarity(clue, word) for word in assassins] + [0])

    maxAllowedCloseness = max(maxBadCloseness + 0.1, maxNeutralCloseness - 0.15, assassinCloseness + 0.2)

    return [goodWord for goodWord in goodWords
            if model.similarity(clue, goodWord) > maxAllowedCloseness]

def clueOnBoard(clue, wordList):
    for word in wordList:
        if clue.lower() in word.lower() or word.lower() in clue.lower():
            return True
    return False

def clueSearch(potentialClues, goodWords, badWords, neutralWords, assassins):
    cluesByNumHintedAt = [[] for _ in range(10)]
    clueObjectList = []
    for clue in potentialClues:
        if clueOnBoard(clue, goodWords + badWords + neutralWords + assassins):
            continue
        wordsHintedAt = getWordsHintedAt(clue, goodWords, badWords, neutralWords, assassins)
        if len(wordsHintedAt) == 0:
            continue
        
        hintRatings = [model.similarity(clue, hintedAt) for hintedAt in wordsHintedAt]
        clueObjectList.append({
            'clue': clue,
            'wordsHintedAt': wordsHintedAt,
            'rating': float(sum(hintRatings)),
        })
    #     cluesByNumHintedAt[len(wordsHintedAt)].append({
    #         'clue': clue,
    #         'wordsHintedAt': wordsHintedAt,
    #         'rating': float(sum(hintRatings)/len(hintRatings)),
    #     })
    #
    # for clueList in cluesByNumHintedAt:
    #     clueList.sort(key=itemgetter('rating'), reverse=True)
    # for i in range(len(cluesByNumHintedAt)):
    #     cluesByNumHintedAt[i] = cluesByNumHintedAt[i][:6]
    # return cluesByNumHintedAt

    clueObjectList.sort(key=itemgetter('rating'), reverse=True)
    clueObjectList.sort(key=lambda wordObject: len(wordObject['wordsHintedAt']), reverse=True)
    return clueObjectList[:10]

def getClues(wordObjectList, team):
    redWords = []
    blueWords = []
    neutralWords = []
    assassins = []

    for wordObject in wordObjectList:
        word = wordObject['word']
        word = '_'.join(word.split())
        if word.lower() in model:
            word = word.lower()
        elif word.title() in model:
            word = word.title()
        else:
            raise ValueError('Invalid Word: ' + word)

        if wordObject['stillOnBoard']:
            label = wordObject['label']
            if label == 'R':
                redWords.append(word)
            elif label == 'B':
                blueWords.append(word)
            elif label =='N':
                neutralWords.append(word)
            elif label == 'A':
                assassins.append(word)

    print(redWords)
    print(blueWords)
    print(neutralWords)
    print(assassins)
    print(team)

    potentialClues = list(model.vocab.keys())[:10000]

    if team == 'red':
        searchResults = clueSearch(potentialClues, redWords, blueWords, neutralWords, assassins)
    else:
        searchResults = clueSearch(potentialClues, blueWords, redWords, neutralWords, assassins)
    return searchResults

if __name__ == '__main__':
    while True:
        word = input()
        print(word in model)