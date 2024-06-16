import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))

import re
import random
import grpc
import yaml

import store_pb2
import store_pb2_grpc

from exceptions import ExitException

# Loads centralized configuration
with open('decentralized_config.yaml', 'r') as conf:
    configuration = yaml.safe_load(conf)

stubs = []
stubs_available = []

for config in configuration['nodes']:
    channel = grpc.insecure_channel(f"{config['ip']}:{config['port']}")
    stub = store_pb2_grpc.KeyValueStoreStub(channel)
    stubs.append(stub)
    stubs_available.append(f"{config['ip']}:{config['port']}")

def clear_screen():
    os.system('clear')

def get_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        exit_decentralized()
    
def put(stub, key, value):
    request = store_pb2.PutRequest(key=key, value=value)
    response = stub.put(request)
    return response.success

def get(stub, key):
    request = store_pb2.GetRequest(key=key)
    response = stub.get(request)
    return response.value, response.found

def slow_down(stub, seconds):
    request = store_pb2.SlowDownRequest(seconds=seconds)
    response = stub.slowDown(request)
    return response.success

def restore(stub):
    request = store_pb2.RestoreRequest()
    response = stub.restore(request)
    return response.success

def put_request():
    global stubs

    while True:
        clear_screen()
        print('PUT REQUEST\n')
        info = get_input("\n[+] Introduce the key:value tuple (Type exit to return) -> ")
        if info:
            # Verify the text:text correctness
            if info == "exit":
                return
            if re.match(r"^.+:.+$", info):
                key, value = info.strip().split(':')
                response = put(random.choice(stubs), key, value)
                break

    if response:
        print(f'The {key}:{value} tuple was correctly stored.')
    else:
        print('Something went wrong.')

    get_input("Press Enter to continue...")
    return

def get_request():
    global stubs_available

    while True:
        clear_screen()
        print('GET REQUEST\n')
        key = get_input("\n[+] Introduce the key you want to search (Type exit to return) -> ")
        if key == "exit":
            return
        if key:
            value, found = get(random.choice(stubs), key)
            break
    
    if found == True:
        print(f"The value relatet to key {key} is: {value}")
    else:
        print('Couldn\'t find the value.')

    get_input("Press Enter to continue...")
    return

def slow_down_request():
    global stubs_available

    while True:
        clear_screen()
        print('SLOW DOWN NODE\n')
        print(f'Available nodes: {stubs_available}')
        port = get_input("\n[+] Type the node you want to slow down (Type exit to return) -> ")
        
        if port == "exit":
            return
        if port in stubs_available:
            index = stubs_available.index(port)
            seconds = get_input(f"\n[+] How many seconds you want to slow down node {port}? ")
            if seconds.isdigit():
                seconds = int(seconds)
                response = slow_down(stubs[index], seconds)
                break

    if response == True:
        print(f"The node {port} has been slowed down {seconds} seconds.")
    else:
        print('Something went worng')

    get_input("Press Enter to continue...")
    return

def restore_request():
    global stubs_available

    while True:
        clear_screen()
        print('RESTORE NODE\n')
        print(f'Available nodes: {stubs_available}')
        port = get_input("\n[+] Type the node you want to restore(Type exit to return) -> ")

        if port == "exit":
            return
        if port in stubs_available:
            index = stubs_available.index(port)
            response = restore(stubs[index])
            break
    
    if response == True:
        print(f"The node {port} has been restores successfully")
    else:
        print('Something went worng')

    get_input("Press Enter to continue...")
    return

def exit_decentralized():
    raise ExitException()

def print_menu():
    clear_screen()
    print("------------------------\n| DECENTRALIZED SYSTEM |\n------------------------")
    print("\n[1] Make put request")
    print("[2] Make get request")
    print("[3] Slow down node")
    print("[4] Restore slowed down node")
    print("[5] Exit")


def main():
    menu_options = {
        1: put_request,
        2: get_request,
        3: slow_down_request,
        4: restore_request,
        5: exit_decentralized
    }

    try:
        while True:
            clear_screen()
            print_menu()
            choice = get_input("\n[+] Enter your choice: ")
            if choice.isdigit() and int(choice) in menu_options:
                menu_options[int(choice)]()
            else:
                print("\n[!] Invalid choice. Please enter a number between 1 and 3.")
                get_input("Press Enter to continue...")
    except ExitException:
        pass

if __name__ == "__main__":
    main()