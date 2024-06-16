#!/bin/bash

# Function to create a virtual environment if it doesn't exist
create_virtualenv() {
    env_name=$1
    created=false
    echo "Checking if virtual environment exists..."
    if [ ! -d "$env_name" ]; then
        echo "Virtual environment not found. Creating..."
        python3 -m venv "$env_name"
        if [ $? -ne 0 ]; then
            echo "python3-venv not found. Installing..."
            sudo apt-get update
            sudo apt-get install -y python3-venv
            if [ $? -eq 0 ]; then
                echo "python3-venv installed. Creating virtual environment..."
                python3 -m venv "$env_name"
            else
                echo "Error during python3-venv installation."
                exit 1
            fi
        fi
        echo "Virtual environment created successfully."
        created=true
    else
        echo "Virtual environment already exists."
    fi
}

# Function to install requirements
install_requirements() {
    env_name=$1
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "Dependencies installed from requirements.txt."
    else
        echo "Failed to install dependencies."
        exit 1
    fi    
}

env_name="SD-env"
created=false

create_virtualenv "$env_name"
source "$env_name/bin/activate"
if $created; then
    install_requirements "$env_name"
fi
