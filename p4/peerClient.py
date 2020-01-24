# peerClient
from collections import OrderedDict
import argparse
import binascii
from socket import *
import Crypto
import Crypto.Random
import random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import pickle
from hashlib import *
import json
import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from random import randint

MINING_REWARD = 20
node_Table = {0:'127.0.0.1:5000',1:'127.0.0.1:5001',2:'127.0.0.1:5002',3:'127.0.0.1:5003'}

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



class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 5

    def __init__(self, identifier):
        self.communication = 0
        self.percentage = 0
        self.money = 0
        self.unconfirmed_transactions = []
        self.chain = []
        self.id = identifier
        print('Hey, my ID is {0}'.format(self.id))
        self.stake = []
        self.register()
        self.read_stake_from_tracker()
        self.get_chain()
        #self.calculate_percentage()
    def write_to_local(self):
        data = pickle.dumps(self.chain)
        with open ('chain.pkl', 'wb') as f:
            f.write(data)
        f.close()
    def register(self):
        message = 'Register '+str(self.id)+ ' 0\r\n\r\n'
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('127.0.0.1',8000))
        client_socket.send(message.encode())
        client_socket.close()
        print('Registered with the tracker.....')
        self.communication+=1

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], time.time(), "0",difficulty)
        genesis_block.hash = genesis_block.compute_hash()
        #self.chain.append(genesis_block)
        #self.log_blockchain()
        self.check_with_tracker_if_mined(genesis_block)

    # GET peers from the tracker
    def read_stake_from_tracker(self):
        self.communication+=1
        self.stake = []
        message = 'Peer\r\n\r\n'
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('127.0.0.1',8000))
        client_socket.send(message.encode())
        print('Now downloading peer information from the tracker...')
        response = client_socket.recv(1024).decode().split('\r\n\r\n')[0]
    	#print('asdsadsads')
    	#print(response)
        client_socket.close()
        if 'NAK' in response:
            print("No peers in tracker")
            return
        response = response.split('\n')
        print(response)
        for pair in response:
            if len(pair.split(' ')) <2:
                continue
            n = pair.split(' ')[0]
            s = pair.split(' ')[1]
            self.stake.append((n,s))
        print(self.stake)
        self.calculate_percentage()

    def calculate_percentage(self):
        total = 0
        for item in self.stake:
            total += int(item[1])
            print(item[0], self.id)
            if str(item[0]) == str(self.id):
                self.money = int(item[1])

        if total != 0:
            self.percentage = self.money/(total *1.0)
        else:
            self.percentage = 0
        print(self.percentage)



    def update_stake_in_tracker(self):
        self.communication+=1
        message = 'Update '+str(self.id) +' ' +str(self.money)+'\r\n\r\n'
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('127.0.0.1',8000))
        client_socket.send(message.encode())
        client_socket.close()

    # def report_block_in_tracker(self, block):
    # 	message = 'Block '+str(block.index)
    # 	client_socket = socket(AF_INET, SOCK_STREAM)
    #     client_socket.connect(('127.0.0.1',8000))
    #     client_socket.send(message.encode())
    #     response = client_socket.recv(1024).decode()
    #     client_socket.close()
    #     return response
    def get_chain(self):
        self.communication+=1
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('127.0.0.1',8000))
        message = b'Chain\r\n\r\n'
        client_socket.send(message)
        f = open ('chain.pkl', 'wb')
        data = client_socket.recv(4096)
        while len(data):
            f.write(data)
            data = client_socket.recv(4096)
        f.close()
        with open ('chain.pkl', 'rb') as f:
            self.chain = pickle.load(f)
        f.close()

        print(len(self.chain))
        #print(self.chain[-1].index)
        print('Got the newest chain....')

    def check_with_tracker_if_mined(self, new_block):
        self.communication+=1
        time_to_start = time.time()
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('127.0.0.1',8000))
        message = 'Check\r\n\r\n'.encode() + pickle.dumps(new_block)
        client_socket.send(message)
        res = client_socket.recv(4096).decode()
        client_socket.close()
        if 'ACK' in res:
            time_to_end   = time.time()
            print('Block {0} has been accepted by all nodes.\n Broadcasting time is {1}'.format(new_block.index, time_to_end - time_to_start))
            self.money += MINING_REWARD
            self.chain.append(new_block)
            self.write_to_local()
            self.update_stake_in_tracker()
        else:
            print('Block {0} has been mined by other node.\n'.format(new_block.index))
            print('Updating the chain....')
            self.get_chain()
	# def broadcast(self, new_block):
	#     time_to_start = time.time()

	#     flag = 0

	#     for i in range(4):
	#     	node = node_Table[i]
	#     	ip = node.split(':')[0]
	#     	port = int(node.split(':')[1])

	#     	if port == int(self.id):
	#     		continue

	#     	client_socket = socket(AF_INET, SOCK_STREAM)

	#         client_socket.connect((ip,port))

	#         message = b'Block\r\n\r\n'
	#         data_string = pickle.dumps(new_block)

	#         client_socket.send(message+data_string)

	#         response = client_socket.recv(1024).decode()
	#         if 'OK' in response:
	#         	flag += 1
	#         client_socket.close()

	#     time_to_end   = time.time()

	#     if flag == 3:
	#     	print('Block {0} has been accepted by all nodes.\n Broadcasting time is {1}'.format(new_block.index, time_to_end - time_to_starto))
	#     	#self.log_blockchain()

	# def log_blockchain(self):
	# 	with open('blockchain.pkl', 'wb') as f:
	# 		pickle.dump(self.chain, f, pickle.HIGHEST_PROTOCOL)
	# 	f.close()

    @property
    def last_block(self):
        return self.chain[-1]
    def add_block_pos(self, block):
    	self.chain.append(block)
    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.compute_hash()

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        #print('HERE NOW')
        self.chain.append(block)
        #self.log_blockchain()
        return True

    def proof_of_work(self, block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        #diff = block.diff
        #iterr = 60
        timer1 = time.time()
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
            timer2 = time.time()

            #if (block.nonce - 1) % iterr == 0:
            if int(timer2 - timer1) % 120 == 0 :#or int(timer2 - timer1) == 121 or int(timer2 - timer1) == 122:
                self.get_chain()
                if self.check_if_mined(block.index):
                    break

        return computed_hash

    def proof_of_work_stake(self, block):

        block.nonce = 0

        diff = int(block.diff * (1 - self.percentage))
        print('difficulty for node {0} is {1}'.format(self.id, diff))
        #iterr = 60
        timer1 = time.time()

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * diff):
            block.nonce += 1
            computed_hash = block.compute_hash()
            timer2 = time.time()
            #if (block.nonce -1) % iterr == 0:
            if int(timer2 - timer1) % 120 == 0 :#if int(timer2 - timer1) == 120 or int(timer2 - timer1) == 121 or int(timer2 - timer1) == 122:
                self.get_chain()
                if self.check_if_mined(block.index):
                    break

        return computed_hash

    # def add_new_transaction(self, transaction):
    #     self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):

        #return (block_hash.startswith('0' * Blockchain.difficulty) and
        return (block_hash.startswith('0' * block.get_diff()) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result


    # def check_if_mined(self, index):
    # 	for block in self.chain:
    # 		if block.index >= index:
    # 			return True
    # 	return False
    def check_if_mined(self, index):
        last_index = self.chain[-1].index
        if last_index >= index:
            print(last_index, index)
            return True
        return False

    def mine_pow(self):

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash(),
                          diff=Blockchain.difficulty)

        proof = self.proof_of_work(new_block)
        
        if proof == None:
            print("Block {0} is mined by other node".format(new_block.index))
            return None
        if not self.check_if_mined(new_block.index):
            print("Block {0} is mined by node {1}".format(new_block.index, self.id))
            print("Now check the block {0} with the tracker first".format(new_block.index))
            #self.add_block(new_block, proof)
            self.unconfirmed_transactions = []
            self.check_with_tracker_if_mined(new_block)
            return new_block.index
        else:
            return None

    def mine_pow_pos(self):
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash(),
                          diff=(int(Blockchain.difficulty * (1 - self.percentage))))
        
        proof = self.proof_of_work_stake(new_block)
        if proof == None:
            print("Block {0} is mined by other node".format(new_block.index))
            return

        if not self.check_if_mined(new_block.index):
            print("Block {0} is mined by node {1}".format(new_block.index, self.id))
            print("Now check the block {0} with the tracker first".format(new_block.index))
            #self.add_block(new_block, proof)
            self.unconfirmed_transactions = []
            self.check_with_tracker_if_mined(new_block)
    
    def mine_pos(self):
        time.sleep(20)
        x = random.randint(1, 300)

        self.read_stake_from_tracker()
        maxx = int(self.stake[-1][1])
        node = self.stake[-1][0]
        print('in POS now')
        for pair in self.stake:
            if int(pair[1]) >= maxx:
                node = pair[0]
                maxx = int(pair[1])
        print(node, maxx)
        print(self.id, node)
        if (str(self.id) == str(node) or x % 5 == 0) and self.percentage < 0.5:
            last_block = self.last_block
            new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash(),
                          diff=Blockchain.difficulty)
            if not self.check_if_mined(new_block.index):
                print("Block {0} is mined by node {1}".format(new_block.index, self.id))
                print("Now check the block {0} with the tracker first".format(new_block.index))
                #self.add_block_pos(new_block)
                self.unconfirmed_transactions = []
                self.check_with_tracker_if_mined(new_block)
        else:
            self.get_chain()
            print("You are not selected by the POS algorithm")


    	


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='python peerClient.py -p CLIENT_PORT')
    parser.add_argument('-p', type=int, dest='port', help='Port # for client')
    #parser.add_argument('--ip', dest='ip',help='IP address for Client')
    args = parser.parse_args()

    chain = Blockchain(args.port)

    i = int(input('Press 1 to mine with POW\nPress 2 to mine with POS\nPress 3 to mine with POS and POW\nPress -1 to exit\n'))
    x = i
    while i != -1:
        if i == -1:
            break
        if i == 1:
        	chain.mine_pow()
        if i == 2:
        	chain.mine_pos()
        if i == 3:
        	chain.mine_pow_pos()

        i = x
        if chain.chain[-1].index >= 20:
            print('total communication is ', chain.communication)
            break
        #i = int(input('Press 1 to mine with POW\nPress 2 to mine with POS\nPress 3 to mine with POS and POW\nPress -1 to exit\n'))