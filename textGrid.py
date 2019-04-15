import re

'''
	TextGrid
		tiers: Object of type Tiers
		raw: raw content of the textgrid

	Tiers
		tiers: Dict with key tier name, value, Tier object
		xmin: float
		xmax: float
		size: integer

		getAnnotations(tier, start, end) -> gets the annotations between start and end
		return is an array of type Annotation

	Tier
		xmin: float
		xmax: float
		name: string
		type: point or interval
		size: integer
		annotations = array of type Annotation

	Annotation
		xmin: float
		xmax: float
		features: Object of type Features

		getFeature(featureName) -> gets the value of the specified feature. 
		returns string since it can be a float or a string.

	Features
		head: string, head. Can be none
		features: dict with key feature name and value, feature value
		rawFeatures: raw string as found in the textgrid
'''

class TextGrid:

	def __init__(self, path):
		self.loadTextGrid(path)

	def loadTextGrid(self, path):
		fd = open(path,"r")
		raw = fd.read()
		self.raw = raw
		fd.close()

		lines = raw.split("\n")
		start = float(lines[3].split(" = ")[1])
		end = float(lines[4].split(" = ")[1])
		
		self.tiers = Tiers(start, end)

		items = re.split(r'item \[[0-9]*\]', raw)[2:]
		for item in items:
			self.loadTier(item)

	def loadTier(self, raw):
		tierLines = raw.split("\n")[1:]
		name = tierLines[1].strip().split(" = ")[1].replace('"',"")
		start = float(tierLines[2].strip().split(" = ")[1])
		end = float(tierLines[3].strip().split(" = ")[1])

		tierType = ""
		
		if "points" in tierLines[4]:
			tierType = "point"
			points = re.split(r'points \[[0-9]*\]', raw)[1:]
			tier = Tier(name, start, end, tierType)
			self.loadAnnotations(tier, points)
		else:
			tierType = "interval"
			intervals = re.split(r'intervals \[[0-9]*\]', raw)[1:]
			tier = Tier(name, start, end, tierType)
			self.loadAnnotations(tier,intervals)

		self.tiers.addTier(name, tier)

	def loadAnnotations(self, tier, annotationList):
		for ann in annotationList:
			annLines = ann.strip().split("\n")[1:]
			end = None
			features = None
			start = float(annLines[0].strip().split(" = ")[1])

			#point
			if len(annLines) == 2:
				end = start
				features = annLines[1].strip().split("mark = ")[1]

			#interval
			elif len(annLines) == 3:
				end = float(annLines[1].strip().split(" = ")[1])
				features = annLines[2].strip().split("text = ")[1]

			iAnn = Annotation(start, end, features)
			tier.addAnnotation(iAnn)

	def getAnnotations(self, tier, start, end):
		return self.tiers.getAnnotations(tier, start, end)

	def writeTextGrid(self, path):
		#ToDo
		pass

class Tiers():

	def __init__(self, start, end):
		self.tiers = {}
		self.xmin = start
		self.xmax = end
		self.size = 0

	def addTier(self, name, tier):
		self.tiers[name] = tier
		self.size +=1

	def getTier(self, name):
		return self.tiers[name]

	def getAnnotations(self, targetTier, start, end):
		return self.tiers[targetTier].getAnnotations(start, end)


class Tier():

	def __init__(self, name, start, end, tierType):	
		self.xmin = start
		self.xmax = end
		self.name = name
		self.type = tierType
		self.size = 0
		self.annotations = []

	def addAnnotation(self, annotation):
		self.annotations.append(annotation)
		self.size +=1

	def getAnnotations(self, start, end):
		anns = []

		for annotation in self.annotations:
			if annotation.xmin >= start and annotation.xmax <= end:
				anns.append(annotation)

		return anns

class Annotation():

	def __init__(self, start, end, rawFeatures=None, head=None, features=None):
		self.xmin = start
		self.xmax = end
		if features:
			self.features = Features(features=features, head=head)
		else:
			self.features = Features(rawFeatures=rawFeatures)

	def getFeature(self, featureName):
		return self.features.getFeature(featureName)

	def addFeature(self, key, value):
		self.features.addFeature(key, value)

	def __str__(self):
		return "Start:"+str(self.xmin)+ " End:"+str(self.xmax)+ " "+ str(self.features)

	def __repr__(self):
		return "Start:"+str(self.xmin)+ " End:"+str(self.xmax)+ " "+ str(self.features)

class Features():

	def __init__(self, rawFeatures=None, features=None, head=None):
		self.features = {}
		self.head = None
		if features:
			self.features = features

		if head:
			self.head = head

		if rawFeatures:
			self.rawFeatures = rawFeatures
			self.extractFeatures()

	def extractFeatures(self):
		if self.rawFeatures == '""':
			pass
		
		elif "{" not in self.rawFeatures:
			self.head = self.rawFeatures.replace('"',"")
		
		else:
			cleanFeats = self.rawFeatures.replace('"',"")
			cleanFeats = cleanFeats.replace("}","")
			cleanFeats = cleanFeats.replace(" ","")
			pieces = cleanFeats.split("{")
			if pieces[0] != '"':
				self.head = pieces[0].replace('"',"")
			
			pieces = pieces[1].split(",")
			
			for feat in pieces:
				key, value = feat.split("=")
				self.features[key] = value

	def getFeature(self, feature):
		result = None
		if feature in self.features.keys():
			result = self.features[feature]
		
		return result

	def addFeature(self, key, value):
		self.features[key] = value
			
	def __str__(self):
		if self.head:
			return "HEAD:"+self.head + " FEATURES:" + str(self.features) 
		else:
			return "HEAD:No Head" + " FEATURES:" + str(self.features) 


	def __repr__(self):
		if self.head:
			return "HEAD:"+self.head + " FEATURES:" + str(self.features) 
		else:
			return "HEAD:No Head" + " FEATURES:" + str(self.features) 

if __name__ == '__main__':

	iT = TextGrid("sample.TextGrid")

	#get me the IP annotations from 0 to 5.5
	print(iT.getAnnotations("IP",0,5.5))
	anns = iT.getAnnotations("IP",0,5.5)

	#get me the phone_mean of each found annotation
	for ann in anns:
		print(ann.getFeature("phone_mean"))