import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

from random import seed
from random import random
from random import shuffle
from random import randint

import threading
from time import localtime
from time import sleep
from datetime import datetime
from os import system

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

p = 0.8
interval = 3
CHAINS = 10

class Blockchain:
    def __init__(self, chain_id):
        self.current_transactions = []
        self.chain = []
        # self.voterchains = [[] for i in range(voterchains)]
        self.nodes = set()
        self.chain_id = chain_id
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # print(f'{last_block}')
            # print(f'{block}')
            # print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = list(self.nodes)
        shuffle(neighbours)
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.post(f'http://{node}/chain', json={'chain_id': self.chain_id})

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
         
        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def common_chain_length(self, chain_id):
        neighbours = self.nodes
        chains = []
        print("hi1")
        print(self.nodes)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            print("hi2")
            response = requests.post(f'http://{node}/chain', json={'chain_id': chain_id})
            print({'chain_id': chain_id})
            print(response.status_code)
            if response.status_code == 200:
                print(response.json())
                chain = response.json()['chain']
                chains.append(chain)

        cur = 0
        while cur < len(self.chain):
            same = True
            for chain in chains:
                if cur < len(chain) and chain[cur] != self.chain[cur]:
                    same = False
                    break
            if not same:
                break
            cur = cur + 1

        return cur + 1

# Instantiate the Node
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
# blockchain = Blockchain()
blockchains = [Blockchain(i) for i in range(CHAINS)]

def mine_func(port, chain_id):
    r = random()
    if r >= p:
        response = {
        'message': "Failed to mine"
        }
        return response
    # chain_id = int(random() * 100000) % CHAINS
    print (str(port-5000) + ": Success!")
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchains[chain_id].last_block
    proof = blockchains[chain_id].proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchains[chain_id].new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchains[chain_id].hash(last_block)
    block = blockchains[chain_id].new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'chain_id' : chain_id
    }
    return response
    

@app.route('/mine', methods=['GET'])
def mine():
    response = mine_func(request)
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['POST'])
def full_chain():
    values = request.get_json()
    print("Values")
    print(values)

    # Check that the required fields are in the POST'ed data
    required = ['chain_id']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    response = {
        'chain': blockchains[values['chain_id']].chain,
        'length': len(blockchains[values['chain_id']].chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    print(values)

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for blockchain in blockchains:
        for node in nodes:
            blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


def consensus_func():
    response = []
    for blockchain in blockchains:
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response.append({
                'message': 'Our chain was replaced',
                'new_chain': blockchain.chain
            })
        else:
            response.append({
                'message': 'Our chain is authoritative',
                'chain': blockchain.chain
            })

    return response

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    response = consensus_func()
    return jsonify(response), 200


def try_mine(port):
    sleep(10)
    chain_id = randint(0, CHAINS-1)
    length = blockchains[chain_id].common_chain_length(chain_id)
    start = datetime.now()
    # outfile = None
    # if port == 5000:
    #     outfile = open("output.txt", "w")
    while True:
        sec = localtime().tm_sec
        now = datetime.now()
        if sec % interval == 0:
            print(str(port-5000)+": Trying to mine")
            mine_func(port, chain_id)
            sleep(1)
            consensus_func()
            sleep(1)
            if port == 5000:
                new_length = blockchains[chain_id].common_chain_length(chain_id)
                if new_length > length:
                    length = new_length
                    elapsed = now - start
                    # with open("outfile.txt", "a") as outfile:
                    #     outfile.write(str(length) + ": " + str(elapsed.seconds) + "\n")
                    # print("SAME SIZE: %d: %d" %(length, elapsed.seconds) )
                    system("echo %d, %d >> output.txt" % (length, elapsed.seconds))

            
            
#def start_app():

    
    
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    #app.run(host='0.0.0.0', port=port)
    
    webapp = threading.Thread(target=app.run, args=('0.0.0.0', port))
    mining = threading.Thread(target=try_mine, args=(port,))
    
    webapp.start()
    mining.start()
    #app.run(host='0.0.0.0', port=port)
