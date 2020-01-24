#tracker for blockchain

from socket import *
from argparse import ArgumentParser
import pickle
import time
import threading

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




chain = []

def write_to_local():
    global chain
    data = pickle.dumps(chain)
    with open ('chain.pkl', 'wb') as f:
        f.write(data)
    f.close()



class determingThread(threading.Thread):
    def __init__(self, csocket,caddr ):
        threading.Thread.__init__(self)
        self.server = csocket
        self.addr = caddr



    # Chain\r\n\r\n
    def send_chain(self):
        global chain
        
        data = pickle.dumps(chain)
        self.server.send(data)
        #self.server.send('\r\n\r\n'.encode())



    # Check\r\n\r\nnew_block
    def check_if_mined(self, block):
        with open ('tem_block.pkl', 'wb') as f:
            f.write(block)
        f.close()
        with open ('tem_block.pkl', 'rb') as f:
            new_block = pickle.load(f)
        f.close()
        #new_block = pickle.load(block)
        index = new_block.index
        #index = message.split('\r\n\r\n')[0].split(' ')[1]
        #index = int(index)
        print(index)

        global chain
        flag = 0
        for block in chain:
            if block.index == index:
                self.server.send('NAK\r\n\r\n'.encode())
                flag = 1
                break
        if flag == 0:
            chain.append(new_block)

            self.server.send('ACK\r\n\r\n'.encode())
            write_to_local()

    # Register 8008 0\r\n\r\n
    def register_node(self, message):
        # log the node
        node = message.split('\r\n\r\n')[0].split(' ')[1:]
        print(node)
        s = ' '
        s = s.join(node) + '\r\n'
        node = s.split(' ')[0]
        print(s)
        print(node)
        try:
            flag = 0
            f = open('stake.txt', 'r')
            lines = f.readlines()
            print(lines)
            f.close()
            for line in lines:
                if node in line:
                    flag = 1
                    break
            if flag == 1:
                print("{0} record already in log ---- Done".format(node))
            else:
                f = open('stake.txt', 'a')
                f.write(s)
                f.close()
        except:
            f = open('stake.txt', 'w')
            f.write(s)
            f.close()

    def send_peers(self):
        try:
            f = open('stake.txt', 'r')
            lines = f.readlines()
            f.close()

            print(lines)
            s = ""
            s = s.join(lines)
            print(s)
            s = s + '\r\n'
            self.server.send(s.encode())
        except:
            self.server.send("NAK\r\n\r\n".encode())

    # Update 8008 100\r\n\r\n
    def Update_stake(self, message):
        node = message.split('\r\n\r\n')[0].split(' ')[1:]
        print(node)
        s = ' '
        s = s.join(node)
        node = s.split(' ')[0]
        stake = s.split(' ')[1]
        s = s + '\r\n'
        print(s)
        print(node)
        print(stake)
        try:
            flag = 0
            f = open('stake.txt', 'r')
            lines = f.readlines()
            print(lines)
            f.close()
            for i in range(len(lines)):
                n = lines[i].split('\r\n')[0].split(' ')[0]
                s = lines[i].split('\r\n')[0].split(' ')[1]
                if node in lines[i] and int(s) is not int(stake):

                    lines[i] = n + ' ' + stake+'\r\n'
                    print(lines[i])
                    flag = 1
                    break
            if flag == 1:
                f = open('stake.txt', 'w')
                f.writelines(lines)
                f.close()
                print("{0} record updated in log ---- Done".format(node))
            # else:
            #     f = open('stake.txt', 'a')
            #     f.write(s)
        except:
            f = open('stake.txt', 'w')
            f.write(s)
            f.close()

    def run(self):
        # connection_socket = socket(AF_INET, SOCK_STREAM)
        # connection_socket.connect((host_name,int(port)))
        message = self.server.recv(2048)
        # Register 127.0.0.1:8008 50\r\n\r\n
        if 'Register'.encode() in message:
            self.register_node(message.decode())
        # Update 127.0.0.1:8008 100\r\n\r\n
        if 'Update'.encode() in message:
            self.Update_stake(message.decode())
            #self.broadcast(winner)
        # Peer\r\n\r\n
        if 'Peer'.encode() in message:
            self.send_peers()
        if 'Check'.encode() in message.split('\r\n\r\n'.encode())[0]:
            self.check_if_mined(message.split('\r\n\r\n'.encode())[1])
        if 'Chain'.encode() in message:
            self.send_chain()
        # if 'Stake' in message:
        #     self.send_stake(message):
        # TODO:
           #  process message from node
           #  message format (node,block# \r\n\r\n)
           #  process which node has right to mine
           #  then write it into a log
           #  read from stake.txt to get data
           #  then feed back to nodes.
           #  then node gets feedback from the server and 
           #  etheir create a block or wait amount of time to listen updates from other nodes.
        #connection_socket.close()
        self.server.close()


def create_first_block():
        global chain
        block = Block(0, [], time.time(), "0", 5)
        chain.append(block)


if __name__ == '__main__':
	
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    create_first_block()
    server_socket = socket(AF_INET, SOCK_STREAM)
    
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    while True:
        server_socket.listen(1)
        print('Ready to serve...')

        connectionSocket, addr = server_socket.accept()
        print('Received a connection from:', addr)
        newThread = determingThread(connectionSocket, addr)
        newThread.start()
    server_socket.close()
# protocol
# 1. register node
	# Register node\r\n\r\n
	# keep records in log
#
# 3. broadcast to all nodes who is the winner for block#
	# winner node\r\n\r\n
	# let every node know who is the winner
# 4. get nodes list from server.
	# list node1\r\nnode2\r\n
	# each node can know each node and get ledger from each node to maintain the longest chain
