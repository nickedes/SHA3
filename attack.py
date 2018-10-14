from main import *


def getreversePrintformat(digest):
	"""
		Input is hex digest
		For example : 1a cc 22 0b 9e 2e a7 20 8d 48 61 ba b4 30 ae 45 b0 fc 48 10 62 1f 19 20 (or) 1acc220b9e2ea7208d4861bab430ae45b0fc4810621f1920
		Return Binary digest
	"""
	out = ""
	for i in range(len(digest)//2):
		out += "{:08b}".format( int( digest[i*2 : (i+1)*2], 16) )[::-1]
	return out


def digestToState(bdigest, w):
	"""
		From digest(binary) construct the state, with rest of lanes being 0 except the lanes with digest
	"""
	filledlanes = bdigest // w

	totalLanes = 25
	bdigest += '0'*(totalLanes - filledlanes)
	A = getState(bdigest, w)

