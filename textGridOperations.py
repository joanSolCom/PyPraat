from textGrid import TextGrid, Tiers, Tier, Annotation, Features

class TextGridOperations:

	def __init__(self, path):
		self.textGrid = TextGrid(path)

	def createAnnotation(self, xmin, xmax, head=None, features=None):
		iAnn = Annotation(xmin, xmax, features=features, head=head)
		return iAnn

	def createTier(self, xmin, xmax, name, tierType=None):
		iTier = Tier(name, xmin, xmax, tierType)
		return iTier

	def addFeatureToAnnotation(self, ann, key, value):
		ann.addFeature(key, value)

	def addAnnotationToTier(self, tier, ann):
		tier.addAnnotation(ann)

	def addTier(self, tierName, tier):
		self.textGrid.tiers.addTier(tierName, tier)

	def getAnnotations(self, tier, start, end):
		return self.textGrid.getAnnotations(tier, start, end)

	def getFeatureFromAnnotation(self, ann, featureName):
		return ann.getFeature(featureName)

if __name__ == '__main__':

	iT = TextGridOperations("sample.TextGrid")
	
	tierName = "MyTier"
	tier = iT.createTier(iT.textGrid.tiers.xmin, iT.textGrid.tiers.xmax, tierName)

	feats = {"feat1":0.1, "feat2":0.3333}
	head = "KPASA"

	ann = iT.createAnnotation(0, 5, features=feats, head=head)
	iT.addFeatureToAnnotation(ann, "feat3",0.123)

	print(iT.getFeatureFromAnnotation(ann, "feat3"))

	ann2 = iT.createAnnotation(5, 10, head="Cabezon")

	iT.addAnnotationToTier(tier, ann)
	iT.addAnnotationToTier(tier, ann2)

	iT.addTier(tierName,tier)

	print(iT.getAnnotations(tierName, 0, 15))
	print(iT.getAnnotations("words",0, 2))