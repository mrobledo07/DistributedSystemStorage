import sys
import os

import centralized_client as cc
import decentralized_client as dc

from exceptions import ExitException

def clear_screen():
    os.system('clear')

def get_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        exit_program()

def connect_to_centralized():
    try:
        cc.main()
    except ExitException:
        pass

def connect_to_decentralized():
    try:
        dc.main()
    except ExitException:
        pass

def exit_program():
    exit(0)

def print_menu():
    clear_screen()
    print("\n[1] Connect to centralized cluster")
    print("[2] Connect to decentralized cluster")
    print("[3] Exit")

def main():
    menu_options = {
        1: connect_to_centralized,
        2: connect_to_decentralized,
        3: exit_program
    }

    while True:
        clear_screen()
        print_menu()
        choice = get_input("\n[+] Enter your choice: ")
        if choice.isdigit() and int(choice) in menu_options:
            menu_options[int(choice)]()
        else:
            print("\n[!] Invalid choice. Please enter a number between 1 and 3.")
            get_input("Press Enter to continue...")

        
if __name__ == "__main__":
    main()