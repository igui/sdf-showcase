'''
Created on 27/01/2010

@author: iavas
'''

from sdf import ItemProcesorPipeline
from time import time, sleep

if __name__ == '__main__':
	def func(k):
		if k % 2 != 0:
			#raise ValueError, "%d not pair" % k
			print("k = %d" % k)
			sleep(0.1)
		else:
			print("k = %d" % k)
	
	start = time()
	pipeline = ItemProcesorPipeline(1)
	for i in range(200):
		pipeline.push(func, i)
	pipeline.wait_end()
	print((time() - start))
	
	start = time()
	for i in range(200):
		func(i)
	print((time() - start))
	
	print("COCOA!")

