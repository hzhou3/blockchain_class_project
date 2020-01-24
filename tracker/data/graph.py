from collections import OrderedDict
import argparse
import binascii
from socket import *
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import pickle
from hashlib import *
import json
from time import *
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from random import randint

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, diff, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.diff = diff
        self.nonce = nonce

    def get_diff(self):
    	return self.diff

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


def get_chain(file):
    with open (file, 'rb') as f:
        chain = pickle.load(f)
    f.close()
    return chain

def print_time(chain):
    for block in chain:
        print(asctime(localtime(block.timestamp)))

def get_stake(file):
	f = open(file, 'r')
	lines = f.readlines()
	f.close()
	stake = []
	communication = []

	for line in lines:
		node = line.split(' ')[0]
		s = line.split(' ')[1]
		stake.append(int(s)/20)
		try:
			c = line.split(' ')[2]
			communication.append(int(c))
		except:
			continue

	return stake, communication

def getTime(chain):
	time = []
	for block in chain:
		time.append(block.timestamp)
	interval = []
	first = time[0]
	for t in time:
		interval.append(t - first)
		first = t
	#print(interval)
	return interval


def getAverageTimePerBlock(file): # Speed 
	time = getTime(get_chain(file))
	return sum(time) / (len(time)-1)


# def getFairness(file):  # fairness and communication
# 	stake, comm = get_stake(file)
# 	return stake, comm

def PlotSpeed(t1, t2, t3):
	import matplotlib.pyplot as plt; plt.rcdefaults()
	import numpy as np
	import matplotlib.pyplot as plt

	objects = ('POW', 'POW+POS', 'POS')
	y_pos = np.arange(len(objects))
	performance = [t1,t2,t3]

	plt.bar(y_pos, performance, align='center', alpha=0.5)
	plt.xticks(y_pos, objects)
	plt.ylabel('Time needed in second')
	plt.title('Time to mine one block')

	plt.show()
	

def PlotFairness(f1, f2, f3):

	import numpy as np
	import matplotlib.pyplot as plt

	import statistics
	std1 = statistics.stdev(f1)
	std2 = statistics.stdev(f2)
	std3 = statistics.stdev(f3)
	std = [std1, std2, std3]
	barWidth = 0.5

	bars1 = f1
	bars2 = f2
	bars3 = f3

	 


	plt.bar([1,2,3,4], bars1, color='green', width=barWidth, edgecolor='white', label='POW')
	plt.bar([6,7,8,9], bars2, color='blue', width=barWidth, edgecolor='white', label='POS+POW')
	plt.bar([11,12,13,14], bars3, color='red', width=barWidth, edgecolor='white', label='POS')


	y_pos = [2.5,7.5,12.5]
	plt.plot(y_pos,std,'go--', linewidth=2, markersize=12,color='black')
	 
	# Add xticks on the middle of the group bars
	plt.xlabel('Fairness', fontweight='bold')
	plt.xticks(y_pos, ['POW', 'POW+POS', 'POS'])
	 
	# Create legend & Show graphic
	plt.legend()


	plt.show()

	

def PlotCommunication(c1, c2, c3):
	c1 = sum(c1)
	c2 = sum(c2)
	c3 = sum(c3)
	import matplotlib.pyplot as plt; plt.rcdefaults()
	import numpy as np
	import matplotlib.pyplot as plt

	objects = ('POW', 'POW+POS', 'POS')
	y_pos = np.arange(len(objects))
	performance = [c1,c2,c3]

	plt.bar(y_pos, performance, align='center', alpha=0.5)
	plt.xticks(y_pos, objects)
	plt.ylabel('Total TCP connections ')
	plt.title('Communication for different mining algorithms (every 2mins get update)')

	plt.show()


t1 = getAverageTimePerBlock('pow_diff7.pkl')
t2 = getAverageTimePerBlock('pos_pow_diff6.pkl')
t3 = getAverageTimePerBlock('pos_wait20_mod5.pkl')
PlotSpeed(t1,t2,t3)


s1, _ = get_stake('pow_diff5.txt')
s2, _ = get_stake('pos_pow_diff6.txt')
s3, _ = get_stake('pos_4_peer.txt')
PlotFairness(s1,s2,s3)


_, c1 = get_stake('pow_diff5.txt')
_, c2 = get_stake('pos_pow_diff5.txt')
_, c3 = get_stake('pos_wait20_mod5.txt')
PlotCommunication(c1,c2,c3)






