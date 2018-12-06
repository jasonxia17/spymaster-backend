from gensim.models import KeyedVectors
from operator import itemgetter
filename = 'GoogleNews-vectors-negative300.bin.gz'
model = KeyedVectors.load_word2vec_format(filename, binary=True, limit=200000)

def getWordsHintedAt(clue, goodWords, badWords, neutralWords, assassin):
    # similar to scoring in curling
    maxBadCloseness = max([model.similarity(clue, badWord) for badWord in badWords])
    maxNeutralCloseness = max([model.similarity(clue, word) for word in neutralWords])
    assassinCloseness = model.similarity(clue, assassin)

    maxAllowedCloseness = max(maxBadCloseness + 0.1, maxNeutralCloseness - 0.15, assassinCloseness + 0.2)

    return [goodWord for goodWord in goodWords
            if model.similarity(clue, goodWord) > maxAllowedCloseness]

def clueSearch(potentialClues, goodWords, badWords, neutralWords, assassin):
    
    # maxWordsHintedAt = max([len(getWordsHintedAt(clue, goodWords, badWords, assasin))
    #                         for clue in potentialClues])
    
    cluesByNumHintedAt = [[] for _ in range(10)]
    clueObjectList = []
    for clue in potentialClues:
        wordsHintedAt = getWordsHintedAt(clue, goodWords, badWords, neutralWords, assassin)
        if len(wordsHintedAt) < 2:
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
    return clueObjectList[:10]

def getClues(wordObjectList, team):
    redWords = []
    blueWords = []
    neutralWords = []
    assassin = ""

    for wordObject in wordObjectList:
        word = wordObject['word']
        label = wordObject['label']
        if wordObject['stillOnBoard']:
            label = wordObject['label']
            if label == 'R':
                redWords.append(word)
            elif label == 'B':
                blueWords.append(word)
            elif label =='N':
                neutralWords.append(word)
            elif label == 'A':
                assassin = word

    print(redWords)
    print(blueWords)
    print(neutralWords)
    print(assassin)
    print(team)

    potentialClues = list(model.vocab.keys())[:10000]

    if team == 'red':
        searchResults = clueSearch(potentialClues, redWords, blueWords, neutralWords, assassin)
    else:
        searchResults = clueSearch(potentialClues, blueWords, redWords, neutralWords, assassin)
    return searchResults
