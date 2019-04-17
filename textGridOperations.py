from textGrid import TextGrid, Tiers, Tier, Annotation
from math import sqrt

class TextGridOperations:

	def __init__(self, path):
		self.textGrid = TextGrid(path)
		self.fricatives = self.loadDictionaries("fricatives.txt")
		self.unvoiced = self.loadDictionaries("unvoiced.txt")
		self.xmin = self.textGrid.tiers.xmin
		self.xmax = self.textGrid.tiers.xmax
		self.computeZscores()
		self.createPromPoints()
		self.createBreakPoints()

	def loadDictionaries(self, path):
		dictlist = []
		fd = open(path,"r")
		lines = fd.readlines()
		for line in lines:
			dictlist.append(line.strip())

		return dictlist

	def computeZscores(self):
		words = self.getAnnotations("words", self.xmin, self.xmax)
		tot = len(words)

		for w in words:
			word_s = w.xmin
			word_e = w.xmax
			if w.head:
				mean = self.z_scorePhone(word_s, word_e)
				w = self.z_scoreIp(w, mean)

	def z_scorePhone(self, start, end):
		phones = self.getAnnotations("phones", start, end)
		
		mean = (end - start)/ len(phones)
		if len(phones) > 2:
			dur_pho = []
			sqr_p = 0
			dev = 0
			for i,p in enumerate(phones):
				head = p.head
				dur_p = p.xmax - p.xmin
				dur_pho.append(dur_p)
				sqr_add = (dur_p - mean)**2
				sqr_p = sqr_p + sqr_add

			if sqr_p != 0:
				cal = sqr_p / len(phones)
				dev = sqrt(cal)
			if dev != 0 and mean != 0:
				for d in dur_pho:
					z_p = (d - mean) / dev
					p.addFeature("z_dur", z_p)

		return mean

	def z_scoreIp(self, word, mean):
		iP = self.getAnnotations("IP", self.xmin, self.xmax)

		ip_start = 0
		ip_end = 0
		for p in iP:
			if word.xmax > p.xmin and (word.xmax < p.xmax or word.xmax == p.xmax) and p.text.features:
				ip_start = p.xmin
				ip_end = p.xmax

		z_dur = 0
		if ip_end != 0:
			ref_ip = self.getAnnotations("IP", ip_start, ip_end)[0]
			ip_mean = ref_ip.text.getFeature("phone_mean")
			ip_std = ref_ip.text.getFeature("phone_std")
			z_dur = (mean - float(ip_mean))/ float(ip_std)
			word.addFeature("z_dur", z_dur)

		return word

	def createPromPoints(self):
		promTier = self.createTier("tones", self.xmin, self.xmax, "point")
		words = self.getAnnotations("words", self.xmin, self.xmax)
		phones = self.getAnnotations("phones", self.xmin, self.xmax)

		for n,w in enumerate(words):
			tot = len(words)
			word_s = w.xmin
			word_e = w.xmax

			if w.head:
				for i,p in enumerate(phones):
					head = p.head
					if head:
						if head[-1] == "1":
							point = ((p.xmax - p.xmin)/2) + p.xmin
							prom = self.createAnnotation(point, point)
							self.addAnnotationToTier(promTier, prom)
			self.addTier("tones", promTier)

		prom_tier = self.getAnnotations("tones", self.xmin, self.xmax)
		prominence = self.prominentWords(words)
		for prom in prom_tier:
			time = prom.xmin

			for idx,l in enumerate(prominence):
				if time > l.xmin and time < l.xmax:
					tobilab = self.tobiAnotation(l)
					promSc = l.text.getFeature("promScore")
					
					prom.head = tobilab
					prom.addFeature("promScore", promSc)

		prom_tier = self.getAnnotations("tones", self.xmin, self.xmax)

	def prominentWords(self, words):
		prominence = []

		prev_f = 0
		prev_i = 0
		prev_d = 0
		for n,w in enumerate(words):
			tot = len(words)
			word_s = w.xmin
			word_e = w.xmax
			head = w.head

			curr_f0 = self.featuresToFloat(w.text.getFeature("z_f0"))
			curr_int = self.featuresToFloat(w.text.getFeature("z_int"))
			z_dur = self.featuresToFloat(w.text.getFeature("z_dur"))

			curr_ave = 0 
			if z_dur and curr_f0 and curr_int:
				if head:
					curr_ave = (curr_f0 + curr_int + z_dur)/3
					w.addFeature("promScore", curr_ave)
				if n != 1:
					if curr_f0 > prev_f and curr_f0 > 0.1:
						prominence.append(w)
					elif curr_f0 <= prev_f and curr_f0 > 0.1:
						prominence.append(w)
					# Secondary prominence detection (based on intensity and duration)
					elif curr_int > prev_i and z_dur > prev_d and curr_ave > 0.1:
						prominence.append(w)
					elif curr_int > prev_i and curr_ave > 0.1:
						prominence.append(w)
					elif prev_d > z_dur and prev_d > 0.1:
						prominence.append(w)
				
				prev_f = curr_f0
				prev_i = curr_int
				prev_d = z_dur

		return prominence

	def featuresToFloat(self,feature):
		if feature != "--undefined--" and feature:
			feature = float(feature) 
		elif feature == "--undefined--":
			feature = None

		return feature


	def tobiAnotation(self, word, idx= None):
		f0 = self.featuresToFloat(word.text.getFeature("z_f0"))
		slope = self.featuresToFloat(word.text.getFeature("slope"))
		range_f = self.featuresToFloat(word.text.getFeature("rangeF0"))
		n_phone = self.featuresToFloat(word.text.getFeature("n_Phones"))

		tobi = ""
		if not idx and slope and f0 and slope < 20 and slope > -20 and f0 > 1:
			tobi = "H*" 
		elif slope and range_f and slope > 20 and range_f > 40 :
			if idx == 4:
				tobi = "L-H%"
			elif idx == 3:
				tobi = "LH-"
			elif idx == None and n_phone > 4:
				tobi = "L*+H"
			elif idx == None and n_phone < 4:
				tobi = "L+H*"
		elif slope and range_f and slope < -20 and range_f > 40:
			if idx == 4:
				tobi = "H-L%"
			elif idx == 3:
				tobi = "HL-"
			elif idx == None:
				tobi = "H*+L"
		elif f0 and f0 > 0.9 and idx == None:
			tobi = "H*"
		elif f0 and f0 > 0.5 and idx == None:
			tobi = "!H*"
		else:
			if idx == 4:
				tobi = "L-L%"
			if idx == 3:
				tobi = "LL-"
			elif idx == None:
				tobi = "L*"

		return tobi

	def createBreakPoints(self):
		breakTier = self.createTier("breaks", self.xmin, self.xmax, "point")
		words = self.getAnnotations("words", self.xmin, self.xmax)

		for w in words:
			point = w.xmax
			br = None

			if w.head:
				br = self.computeBreakFeat(point)
				breakP = self.createAnnotation(point, point)
				breakP.head = br
				self.addAnnotationToTier(breakTier, breakP)
				if br == 3 or br == 4:
					self.addBT(point, br, w)

		self.addTier("breaks", breakTier)

	def addBT(self, time, br, word):
		tones = self.textGrid.getTier("tones")

		tobilab = self.tobiAnotation(word, br)
		bt = self.createAnnotation(time, time)
		bt.head = tobilab
		self.addAnnotationToTier(tones, bt)

	def computeBreakFeat(self, time):
		words = self.getAnnotations("words", self.xmin, self.xmax)
		br = None
		for word in words:
			if word.xmin == time:
				dur = word.xmax - word.xmin
				if word.head == None and dur > 0.05:
					br = 4
				elif word.head == None and dur < 0.05:
					br = 3

		if br == None:
			next_pho = None
			last_phodur = 0
			last_pho = None
			for word in words:
				if word.xmax == time:
					n_phones = int(word.text.getFeature("n_Phones"))
					if n_phones > 4:
						phones = self.getAnnotations("phones", word.xmin, word.xmax)
						for p in phones:
							if p.xmax == word.xmax:
								last_pho = p.head
								last_phodur = p.xmax - p.xmin
					else:
						br = 1
				elif word.xmin == time:
					phones = self.getAnnotations("phones", word.xmin, word.xmax)
					for p in phones:
						if p.xmin == word.xmin:
							next_pho = p.head
			if br == None and next_pho and last_pho:
				match1 = self.matchDict(last_pho)
				match2 = self.matchDict(next_pho)
				if match1 or match2:
					br = 2
			else:
				br = 1

		return br

	def matchDict(self, phone):
		match = False
		if phone in self.fricatives or phone in self.unvoiced:
			match = True

		return match

	def createAnnotation(self, xmin, xmax, head=None, features=None):
		iAnn = Annotation(xmin, xmax, features=features, head=head)
		return iAnn

	def createTier(self, name, xmin, xmax, tierType=None):
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
	path = "/home/upf/Desktop/test/"
	iT = TextGridOperations(path+"0961_5m_mod4.TextGrid")
