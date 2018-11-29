from gensim.models import KeyedVectors
from operator import itemgetter
filename = 'GoogleNews-vectors-negative300.bin.gz'
model = KeyedVectors.load_word2vec_format(filename, binary=True, limit=200000)

def getWordsHintedAt(clue, goodWords, badWords, assasin):
    # similar to scoring in curling
    maxBadCloseness = max([model.similarity(clue, badWord) for badWord in badWords])

    return [goodWord for goodWord in goodWords
            if model.similarity(clue, goodWord) > maxBadCloseness + 0.1]

def clueSearch(potentialClues, goodWords, badWords, assasin):
    
    # maxWordsHintedAt = max([len(getWordsHintedAt(clue, goodWords, badWords, assasin))
    #                         for clue in potentialClues])
    
    cluesByNumHintedAt = [[] for _ in range(10)]

    for clue in potentialClues:
        wordsHintedAt = getWordsHintedAt(clue, goodWords, badWords, assasin)
        if len(wordsHintedAt) < 2:
            continue
        
        hintRatings = [model.similarity(clue, hintedAt) for hintedAt in wordsHintedAt]
        cluesByNumHintedAt[len(wordsHintedAt)].append({
            'clue': clue,
            'wordsHintedAt': wordsHintedAt,
            'rating': float(sum(hintRatings)),
        })
    
    for clueList in cluesByNumHintedAt:
        clueList.sort(key=itemgetter('rating'), reverse=True)
    for i in range(len(cluesByNumHintedAt)):
        cluesByNumHintedAt[i] = cluesByNumHintedAt[i][:6]
    return cluesByNumHintedAt

def getClues(words, labels, team):
    redWords = [words[i] for i in range(25) if labels[i] == 'R']
    blueWords = [words[i] for i in range(25) if labels[i] == 'B']

    potentialClues = list(model.vocab.keys())[:10000]

    if team == 'red':
        searchResults = clueSearch(potentialClues, redWords, blueWords, '')
    else:
        searchResults = clueSearch(potentialClues, blueWords, redWords, '')
    return searchResults
