import sys
import os


def createNrcEmotionLexicons (folder):
	global nrcDict
	nrcDict = dict()
	global nrcDictLabels
	nrcDictLabels = ["Anger", "Anticipation", "Disgust", "Fear", "Joy", "Sadness" ,"Surprise", "Trust"]
	for filename in os.listdir(folder):
		nrcDict[filename] = dict()
		with open (os.path.join(folder, filename), 'r') as file:
			for line in file:
				parts = line.replace("\n", "").strip().split("\t")
				# print(parts[0].lower(), parts[3:])
				nrcDict[filename][parts[0].lower()] = (parts[3:])

def createNrcPositiveNegativeLexicons (folder):
	global nrcPosNegDict
	nrcPosNegDict = dict()
	global nrcPosNegDictLabels
	nrcPosNegDictLabels = ["Positive", "Negative"]
	for filename in os.listdir(folder):
		nrcPosNegDict[filename] = dict()
		with open (os.path.join(folder, filename), 'r') as file:
			for line in file:
				parts = line.replace("\n", "").strip().split("\t")
				# print(parts[0].lower(), parts[3:])
				nrcPosNegDict[filename][parts[0].lower()] = (parts[1:3])

def createNrcVadLexicon (folder):
	global nrcVadDict
	nrcVadDict = dict()
	global nrcVadDictLabels
	nrcVadDictLabels = ["Valence", "Arousal", "Dominance"]
	for filename in os.listdir(folder):
		nrcVadDict[filename] = dict()
		with open (os.path.join(folder, filename), 'r') as file:
			for line in file:
				parts = line.replace("\n", "").strip().split("\t")
				# print(parts[0].lower(), parts[3:])
				nrcVadDict[filename][parts[0].lower()] = (parts[1:])


def initializeFeatures(language, myDict, myLexiconList):
	for myLexDict in myLexiconList:

		feats = eval(myLexDict)[language][list(eval(myLexDict)[language].keys())[0]]
		# print(myLexDict, feats)
		for i in range (0,len(feats)):
			myFeat = myLexDict+"_"+eval(myLexDict+"Labels")[i]
			myDict[myFeat] = 0


def countWordsFound(myDict, myLexDict):
	if myLexDict in myDict:
		myDict[myLexDict] = myDict[myLexDict] + 1
	else:
		myDict[myLexDict] = 1

def averageTweetValues(myFeaturesDict, myWordsFoundDict):
		averageDict = dict()
		for k in myWordsFoundDict.keys():
			for i in range(0, len(myFeaturesDict.keys())+1):
				featName = str(k)+str(i)
				if featName in myFeaturesDict:
					averageDict[featName] = myFeaturesDict[featName] / myWordsFoundDict[k]
		return(averageDict)			


def removeDuplicateToken (tokens):
	wordsToProcessList = list(dict.fromkeys(tokens))
	return(wordsToProcessList)

def addToFeatures(myDict, myTag, myFeaturesArray):
		for i in range (0,len(myFeaturesArray)):
			myFeat = myTag+"_"+eval(myTag+"Labels")[i]
			if myFeat in myDict:
				myDict[myFeat]=myDict[myFeat]+float(myFeaturesArray[i])
			else:
				myDict[myFeat]=+float(myFeaturesArray[i])


def extractEmotions(language, text):
			tokens = text.lower().strip().split(" ")
			featuresDict = dict()
			numberOfWordsFoundDict = dict()
			lexiconsList = ["nrcDict","nrcVadDict","nrcPosNegDict"]
			initializeFeatures(language, featuresDict, lexiconsList)
			wordsToProcessList = removeDuplicateToken(tokens)

			for token in wordsToProcessList:
				for lexDict in lexiconsList:
					if token in eval(lexDict)[language]:
						if len(token)<2:
							continue
						# wordsFoundDict[token] = 0
						countWordsFound(numberOfWordsFoundDict, lexDict)
						feats = eval(lexDict)[language][token]
						addToFeatures(featuresDict, lexDict, feats)


			return (featuresDict)

