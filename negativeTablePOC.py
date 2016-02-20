import os
import struct


class crackTree(object):
	""" class that builds a negative lookup tree for hashes for a wordlist """

	# hashmethod must be a method from Python's hashlib
	def __init__(self, hashMethod, debug = True):
		self.debug = debug

		self.hashMethod = hashMethod
		self.hashBytes = self.hashMethod().digest_size

	def createTable(self, inputFile, outputFile):

		self.printDebug("Creating table for file: " + str(inputFile))

		try:
			self.fileSize = os.path.getsize(inputFile)
			assert self.fileSize > 0
		except:
			self.printDebug("Could not get line count for file\n")
			raise

		self.printDebug("Choosing table size..")

		self.useBytes = self.chooseTableSize(self.fileSize)

		self.printDebug("Starting loading wordlist..")

		
		fin = open(inputFile, 'r')
		statusCounter = 0
		
		# todo: directly write to file instead of tmp parameter
		tmp = {}
		for word in fin.readlines():

			word = word.strip("\n")
			theHash = self.hashMethod(word).digest()
			theHash = theHash[:self.useBytes]
			
			tmp[theHash]=0

		fin.close()

		tmp = list(tmp)
		tmp = [self.packtoInt(i) for i in tmp]
		tmp.sort()
		# todo: auto fix 3 en 4 bytes
		tmp = [struct.pack(">I", i) for i in tmp]
		fout = open(outputFile,'wb')
		for i in tmp:
			fout.write(i)
		fout.close()

		fout = open("fileInfo_"+outputFile,'w')
		fout.write("Hash byte size used: " + str(self.useBytes))
		fout.write("\nHash method used: " + str(self.hashMethod))
		
		fout.close()



	def printDebug(self, value):
		if self.debug:
			print value


	def calcChanceTotalCollisions(self, n, m):
		'''
			Calculate total estimated collisions of generating n items for m buckets

			See http://stackoverflow.com/questions/9104504/expected-number-of-hash-collisions
		'''
		n = float(n)
		m = float(m)
		return n - m * (1.00-((m-1.00)/m)**n)

	def chooseTableSize(self, lineCount):
		'''
			Choose size for the table
			Must fill all possible space for less than 50% to get less than 50% false positives
		'''

		for useBytes in range(1,self.hashBytes):

			space = 256**useBytes
			estimatedCollisions = self.calcChanceTotalCollisions(lineCount, space)
			estimatedSpaceUsed = lineCount - estimatedCollisions

			# this is also the chance of false positives
			fillPercentage = float(estimatedSpaceUsed) / float(space)

			if fillPercentage > 0.5:
				continue

			self.printDebug("Using " + str(useBytes) + " bytes gives me " + str(space) + " values of space")
			self.printDebug("I estimate " + str(estimatedCollisions) + " collisions")
			self.printDebug("Leaving about " + str(estimatedSpaceUsed) + " values used")
			self.printDebug("This table will be filled by about " + str(fillPercentage))

			return useBytes
		
	def packtoInt(self, binary):

		while len(binary)%4!=0:
			binary = '\x00' + str(binary)

		# convert to integer
		unpackSize = len(binary) / 4
		binary = sum(struct.unpack('>'+('I'*unpackSize), binary))

		return binary

	def lookupTable(self, inputFile, value, usedBytes):

		lookupInt = self.packtoInt(value)

		fileSize = os.path.getsize(inputFile)

		devider = (fileSize / usedBytes) / 2
		start = devider
		devider = devider / 2

		fin = open(inputFile,'rb')

		while 1:
			currentPoint = start * usedBytes
			fin.seek(currentPoint)

			test = self.packtoInt(fin.read(usedBytes))
			#print str(test) + " vs " + str(lookupInt)

			if test == lookupInt:
				return True
				break
			if devider == 0:
				if test < lookupInt:
					while test < lookupInt:
						currentPoint += usedBytes
						fin.seek(currentPoint)
						test = self.packtoInt(fin.read(usedBytes))
						if test == lookupInt:
							return True
				if test > lookupInt:
					while test > lookupInt:
						currentPoint -= usedBytes
						fin.seek(currentPoint)
						test = self.packtoInt(fin.read(usedBytes))
						if test == lookupInt:
							return True

				return False
				break

			if test < lookupInt:
				start += devider
			else:
				start -= devider

			devider = devider / 2

		fin.close


from hashlib import md5
from datetime import datetime

lolCracktree = crackTree(md5)
lolCracktree.createTable('rockyou.txt', 'dumprockyou')	# comment out this line once the table has been created


print "Performing two lookups"

testword = "test"		# test is a word in the dictionary
lookupHash = md5(testword).digest()
lookupValue = lookupHash[:4]
print lolCracktree.lookupTable('dumprockyou', lookupValue, 4) # will output True

testword = "testWordNotInDict"		# testWordNotInDict is a word not in the dictionary
lookupHash = md5(testword).digest()
lookupValue = lookupHash[:4]
print lolCracktree.lookupTable('dumprockyou', lookupValue, 4) # will output False

