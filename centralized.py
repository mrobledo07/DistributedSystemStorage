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
with open('centralized_config.yaml', 'r') as conf:
    configuration = yaml.safe_load(conf)

# create a class to define the server functions, derived from
# store_pb2_grpc.KeyValueStoreServicer
class KeyValueStoreServicer(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, config):
        self.slave_nodes = set()
        self.delay = 0
        self.responses = set()
        self.file = f"saves/centralized/{config}.txt"
        self.kv_dict = read_file(self.file)

    # Only master node receives put requests, with 2PC the information gets replicated to slave nodes
    def put(self, request, context):
        # 2PC - Phase 1: can commit
        for slave in self.slave_nodes:
            channel = grpc.insecure_channel(slave)
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            response = stub.canCommit(store_pb2.CanCommitPetition(key=request.key))

            if not response.available:    # If some slave node cannot commit, abort
                return store_pb2.PutResponse(success=False)
        
        # 2PC - Phase 2: do commit
        for slave in self.slave_nodes:
            channel = grpc.insecure_channel(slave)
            stub = store_pb2_grpc.KeyValueStoreStub(channel)
            response = (stub.doCommit(store_pb2.PutRequest(key=request.key, value=request.value)))

        # Once all salves have commited, master commits
        persistent_save(request.key, request.value, self.file)
        time.sleep(self.delay)  # Simulates a node delay
        self.kv_dict[request.key] = request.value

        return store_pb2.PutResponse(success=True)
    
    # Any node can get this type of request. Based on a given key, returns its value
    def get(self, request, context):
        time.sleep(self.delay)  # Simulates a node delay
        value = self.kv_dict.get(request.key)
        
        if value:
            response = store_pb2.GetResponse(value=value, found=True)
        else:
            response = store_pb2.GetResponse(value=value, found=False)

        return response

    # First phase of the 2PC protocol. Always returns True for simplicity
    def canCommit(self, request, context):
        return store_pb2.CanCommitResponse(available=True)

    # Second phase of the 2PC protocol. Slave node proceeds to commit the key-value tuple
    def doCommit(self, request, context):
        persistent_save(request.key, request.value, self.file)
        time.sleep(self.delay)
        self.kv_dict[request.key] = request.value

        return store_pb2.HaveCommited(haveCommited=True) 
    
    # Adds X seconds of delay to a node. That is to simulate defective nodes and network partitions
    def slowDown(self, request, context):
        self.delay = request.seconds
        return store_pb2.SlowDownResponse(success=True)
    
    # Removes any seconds of delay a node had
    def restore(self, request, context):
        self.delay = 0
        return store_pb2.RestoreResponse(success=True)

    # A slave node notifies the master node, so it can reach him at 2PC protocol
    def notifyMaster(self, request, context):
        self.slave_nodes.add(request.config)
        return store_pb2.NotifySuccess(success=True)

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
            for line in file:
                if ":" in line:
                    key, value = line.strip().split(':')
                    dictionary[key] = value
    except FileNotFoundError:
        #print(f"Couldn't find the file {file_path}")
        pass

    return dictionary

# Starts master node at given ip and port
def server_master():
    config = f"{configuration['master']['ip']}:{configuration['master']['port']}"

    master = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(config), master)
    master.add_insecure_port(config)
    master.start()
    
    master.wait_for_termination()

# Starts slave node at given ip and port
def server_slave(slave_config):
    config = f"{slave_config['ip']}:{slave_config['port']}"
    
    slave = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(config), slave)
    slave.add_insecure_port(config)
    slave.start()

    # Once the slave node is up, notifies the master node
    channel = grpc.insecure_channel(f"{configuration['master']['ip']}:{configuration['master']['port']}")
    notify_stub = store_pb2_grpc.KeyValueStoreStub(channel)
    response = notify_stub.notifyMaster(store_pb2.SlaveConfiguration(config=config))

    slave.wait_for_termination()


if __name__ == '__main__':
    # Starting master node at port 32770
    master_process = multiprocessing.Process(target=server_master)
    master_process.start()

    # Starting slave nodes at ports 32771 & 32772
    slave_processes = []
    for slave_config in configuration['slaves']:
        slave_process = multiprocessing.Process(target=server_slave, args=(slave_config,))
        slave_processes.append(slave_process)
        slave_process.start()

    master_process.join()
    for slave_process in slave_processes:
        slave_process.join()