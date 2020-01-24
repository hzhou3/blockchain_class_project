This is the project for CSCI 582 Blockchain.

This project test POW, POS and POS+POW in terms of communications, speed and fairness.

To check results graphs, run: python /tracker/data/graph.py

p1 - p4 are peers in the testing blockchain. peerClient.py is for mining blocks in different ways(1 for POW, 2 for POW+POS, and 3 for POS).

Some code in peerClient.py are copied from https://github.com/folkpark/blockchain and http://adilmoujahid.com/posts/2018/03/intro-blockchain-bitcoin-python/

tracker is the server which solve conflicts and communicate with peers.

To run the project:

first run tracker
	*python server.py -p [port_number]
then clients
	*python peerClient.py -p [port_number]

then choose POW, POS or POS+POW to mine blocks.

/tracker/data is a folder which stored all raw data I tested. Then graph.py can generate graphs based on the raw data.




