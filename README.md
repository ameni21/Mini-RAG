# Mini-RAG

This is a minimal implementation of the RAG model for question answering


## Table of Contents
- Requirements
- Installation
- Run the FastAPI server

## (Optional) Steup your command line intrface for better readability
```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Requirements

  Python 3.8 or later

  #### Install Python using pip3

1) install pip 

```bash 
$ sudo apt-get install python3-pip
```

2)  create a new environnement 

```bash
$ python3 -m venv .venv
```

3) Activer l’environnement virtuel 
```bash 
source .venv/bin/activate
```

## Installation


### Install the required packages

```bash 
$ pip install -r requirements.txt
```

### Setup the environment variables
```bash 
$ cp .env.example .env
```
Set your environment variables in the .env file. Like OPENAI_API_KEY value.

### Run Docker Compose Services
```bash 
$ cd docker
$ cp .env.example .env
```
*update .env with your credentials

```bash 
$ cd docker
$ sudo docker compose up -d
```

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

