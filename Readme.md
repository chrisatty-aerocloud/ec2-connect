# EC2 Connect

Create an SSH session or SSH tunnel on an EC2

## Prerequisites

- Python3
- AWS CLI
- AWS authentication - suggest you use AWS SSO

## Installation

- Clone the repository
- Create a python venv `python -m venv .`
- Activate the environment `source ./bin/activate`
- Install pip `python3 -m ensurepip`
- Install the dependencies `pip3 install -r requirements.txt`
- Make script executable `chmod +x connect.py`
- Create an alias in your .bashrc or .zshrc file `alias ec2_connect="<path_to_repo>/bin/python3 <path_to_repo>/connect.py"`
- Restart terminal

## Run

`ec2_connect`

## Help

`ec2_connect --help`