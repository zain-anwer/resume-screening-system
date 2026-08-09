#!/bin/bash

# create and activate virtual environment it it doesn't exist
[ -d ".venv" ] || python -m venv .venv
source .venv/Scripts/activate

# upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# install spacy model
python -m spacy download en_core_web_sm
