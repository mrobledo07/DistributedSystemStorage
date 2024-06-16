# Introduction to the Practice

In this practice, two models of distributed storage systems are developed: the first with a centralized approach and the second with a decentralized approach.

## Centralized System

The cluster of the centralized system consists of three servers, one master and two slaves. Only the master can receive put requests, while get requests can be processed by any node, both master and slaves.

To achieve consistency in this system, the Two-Phase Commit (2PC) protocol is used. In this protocol, we can distinguish two parts: in the first, the master node sends a CanCommit request to the other nodes, and in the second, based on the responses received, it sends a doCommit request in which all nodes commit the received information.

## Decentralized System

In this cluster, there are three servers, all of the same rank, so any node can receive and process both put and get requests.

To achieve consistency in this system, a replication method based on weights and quorum is implemented. Each node in the cluster has an assigned weight, and to respond to put and get requests, a certain quorum must be reached by summing the weights of the nodes that respond affirmatively.

The quorum required for reads is 2 and for writes is 3. Only when the necessary quorum is reached will the client's request be answered.

# Steps for Execution

To run the project, first, execute the `setup_venv.sh` script (superuser permissions are not needed). This script prepares a virtual environment with all the packages necessary for the project's execution. The packages to be installed, along with their versions, are listed in the `requirements.txt` file.

After that you need to activate de enviroment executing the command `source SD-env/bin/activate`

Once the virtual environment is installed and activated, run the command `python3 eval/eval.py` to execute the tests for the centralized and decentralized systems.


# Distributed storage systems and the CAP theorem

```
Project/
│
├── proto/
│   ├── store.proto
│   ├── store_pb2.py
│   └── store_pb2_grpc.py
│
├── centralized_config.yaml
├── decentralized_config.yaml
├── centralized.py
├── decentralized.py
├── eval/
│   ├── test_centralized_system.py
│   └── test_decentralized_system.py
│
└── ...
```

## Directory Structure Explanation

- **proto/**: Contains Protocol Buffer files used for defining gRPC services and messages. Generated Python files (`store_pb2.py` and `store_pb2_grpc.py`) based on `store.proto` should be stored here.

- **centralized_config.yaml and decentralized_config.yaml**: YAML configuration files containing settings for the centralized and decentralized systems.

    - ***Centralized Format***: 

    ```yaml
    master:
      ip: <IP>
      port: <Port>

    slaves:
      - id: <slave_1_ID>
        ip: <slave_1_IP>
        port: <slave_1_Port>
      - id: <slave_2_ID>
        ip: <slave_2_IP>
        port: <slave_2_Port>
      ...
    ```

    - ***Decentralized Format***: 

    ```yaml
    nodes:
      - id: <node_1_ID>
        ip: <node_1_IP>
        port: <node_1_Port>
      - id: <node_2_ID>
        ip: <node_2_IP>
        port: <node_2_Port>
      ...
    ```

- **eval/**: Directory containing evaluation scripts and tests.

  - **test_centralized_system.py**: Script containing unit tests for the centralized system.
  
  - **test_decentralized_system.py**: Script containing unit tests for the decentralized system.

Each component of the project is organized into its respective directory, facilitating clear separation of concerns and ease of navigation. The `eval` directory specifically houses test scripts for evaluating the functionality and correctness of the implemented systems.

> **Note:** Students are required to define the necessary stubs for implementing the Two Phase Commit (2PC) protocol and for node registration in the system. These stubs must be manually added to the store.proto file by the students as part of their implementation.
