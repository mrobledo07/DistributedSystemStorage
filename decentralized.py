import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))

import grpc
import yaml
from concurrent import futures
import multiprocessing
import time

import store_pb2
import store_pb2_grpc

# Loads centralized configuration
with open('decentralized_config.yaml', 'r') as conf:
    config = yaml.safe_load(conf)

# create a class to define the server functions, derived from
# store_pb2_grpc.KeyValueStoreServicer
class KeyValueStoreServicer(store_pb2_grpc.KeyValueStoreServicer):

    def __init__(self, config, weight):
        self.peers = set()
        self.delay = 0
        self.weight = weight    # The amount his vote counts
        self.file = f"saves/decentralized/{config}.txt"
        self.kv_dict = read_file(self.file)

    # Any node can get this type of request. Given a key and a value, 
    # it starts a voting and if succesess sends doCommit(k,v) to all nodes
    def put(self, request, context):
        time.sleep(self.delay)  # Simulates a node delay
        
        quorum_needed = 3
        quorum = 0

        for node in cluster_nodes:  # Sends vote petitions to all nodes
            channel = grpc.insecure_channel(node)
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            response = (stub.askVote(store_pb2.VoteRequest(key=request.key)))
            quorum += response.vote

            if quorum >= quorum_needed:
                break
        
        if quorum >= quorum_needed:  # If the sum of all votes reaches the quorum needed, commits 
            for node in cluster_nodes:
                channel = grpc.insecure_channel(node)
                stub = store_pb2_grpc.KeyValueStoreStub(channel)
                response = (stub.doCommit(store_pb2.PutRequest(key=request.key, value=request.value)))
            
            response = store_pb2.PutResponse(success=True)
        else:
            response = store_pb2.PutResponse(success=False)
            
        return response
    
    # Any node can get this type of request. Based on a given key, returns its value
    def get(self, request, context):
        time.sleep(self.delay)  # Simulates a node delay

        quorum_needed = 2
        quorum = 0

        for node in cluster_nodes:  # Sends vote petitions to all nodes
            channel = grpc.insecure_channel(node)
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            response = (stub.askVote(store_pb2.VoteRequest(key=request.key)))
            quorum += response.vote

            if quorum >= quorum_needed:
                break

        if quorum >= quorum_needed:  # If the sum of all votes reaches the quorum needed, returns the value  
            value = self.kv_dict.get(request.key)
            if value:
                response = store_pb2.GetResponse(value=value, found=True)
            else:
                response = store_pb2.GetResponse(value=value, found=False)
        else:
            response = store_pb2.GetResponse(value=value, found=False)

        return response

    # If voting succeeded, all nodes commit the key-value pair
    def doCommit(self, request, context):
        persistent_save(request.key, request.value, self.file)
        time.sleep(self.delay)
        self.kv_dict[request.key] = request.value 

        return store_pb2.HaveCommited(haveCommited=True) 

    # Returns his own weight as a response of a vote request
    def askVote(self, request, context):
        x = self.weight
        return store_pb2.VoteResponse(vote=self.weight)
    
    # Adds X seconds of delay to a node. That is to simulate defective nodes and network partitions
    def slowDown(self, request, context):
        self.delay = request.seconds
        return store_pb2.SlowDownResponse(success=True)
    
    # Removes any seconds of delay a node had
    def restore(self, request, context):
        self.delay = 0
        return store_pb2.RestoreResponse(success=True)

# Saves the key-value information on a file (saves/<ip>:<port>.txt)
def persistent_save(key, value, file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.readlines()
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            file.write(f"{key}:{value}\n")
        return
    else:
        line_found = False
        for i, line in enumerate(file_content):
            if line.startswith(f"{key}:"):
                file_content[i] = f"{key}:{value}\n"
                line_found = True
                break

    if not line_found:
        file_content.append(f"{key}:{value}\n")

    with open(file_path, 'w') as file:
        file.writelines(file_content)

# Reads content on persistent node text file
def read_file(file_path):
    dictionary = dict()

    try:
        with open(file_path, 'r') as file:
            for i, line in enumerate(file):
                if ":" not in line:
                    del file[i]
            for line in file:
                key, value = line.strip().split(':')
                dictionary[key] = value
    except FileNotFoundError:
        #print(f"Couldn't find the file {file_path}")
        pass

    return dictionary

# Starts node at given ip and port
def server_node(node_config):
    config = f"{node_config['ip']}:{node_config['port']}"
    node = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(config, node_config['weight']), node)
    node.add_insecure_port(config)
    node.start()
    register_on_cluster(config)

    node.wait_for_termination()
    cluster_nodes.remove(config)

# Registers the 'ip:port' of the node on a shared list
def register_on_cluster(node):
    if node not in cluster_nodes:
        cluster_nodes.append(f'{node}')
    else:
        print(f'The node {node} was already registered.')

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    cluster_nodes = manager.list()  # Shared list whit all the 'ip:port' nodes

    node_processes = []
    for node_config in config['nodes']:
        node_process = multiprocessing.Process(target=server_node, args=(node_config,))
        node_processes.append(node_process)
        node_process.start()

    for node in node_processes:
        node.join()