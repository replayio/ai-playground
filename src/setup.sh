#!/bin/bash

# Update package list
sudo apt-get update

# Install system dependencies
sudo apt-get install -y python3-pyaudio

# Install Python packages
pip3 install pyaudio SpeechRecognition

# Any additional setup steps can be added here
