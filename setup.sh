#!/bin/bash

# This script sets up the environment for the AI Playground project.
# It installs necessary dependencies and configures Google Cloud credentials.
#
# IMPORTANT: Before running this script, make sure you have created a .env.secret file
# in the project root directory with your Google Cloud credentials. See README.md for instructions.

# Load Google Cloud credentials from .env.secret
if [ -f .env.secret ]; then
    echo "Loading Google Cloud credentials from .env.secret"
    export $(grep -v '^#' .env.secret | xargs)
else
    echo "Warning: .env.secret file not found. Please create it and add your Google Cloud credentials."
    echo "See README.md for instructions on setting up Google Cloud credentials."
    exit 1
fi

# Check if GOOGLE_APPLICATION_CREDENTIALS is set
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Error: GOOGLE_APPLICATION_CREDENTIALS is not set in .env.secret"
    echo "Please add GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json to .env.secret"
    exit 1
fi

# Check if the credentials file exists
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Error: Google Cloud credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS"
    echo "Please ensure the file exists and the path is correct in .env.secret"
    exit 1
fi

install_package() {
    local package_name="$1"
    local package_manager="$2"

    case "$package_manager" in
        apt-get)
            sudo apt-get update
            sudo apt-get install -y "$package_name"
            ;;
        yum)
            sudo yum install -y "$package_name"
            ;;
        brew)
            brew install "$package_name"
            ;;
        *)
            echo "Unsupported package manager: $package_manager"
            return 1
            ;;
    esac
}

detect_package_manager() {
    case "$OSTYPE" in
        linux-gnu*)
            echo "$(command -v apt-get || command -v yum || echo "unknown")"
            ;;
        darwin*)
            echo "$(command -v brew || echo "unknown")"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

install_ripgrep() {
    if command -v rg &> /dev/null; then
        echo "ripgrep is already installed."
        return 0
    fi

    echo "ripgrep could not be found. Installing..."

    local package_manager=$(detect_package_manager)

    if [ "$package_manager" = "unknown" ]; then
        echo "Unsupported package manager or operating system. Please install ripgrep manually."
        return 1
    fi

    install_package "ripgrep" "${package_manager##*/}"
    echo "ripgrep has been installed successfully."
}

install_graphviz() {
    if command -v dot &> /dev/null; then
        echo "Graphviz is already installed."
        return 0
    fi

    echo "Graphviz could not be found. Installing..."

    local package_manager=$(detect_package_manager)

    if [ "$package_manager" = "unknown" ]; then
        echo "Unsupported package manager or operating system. Please install Graphviz manually."
        return 1
    fi

    install_package "graphviz" "${package_manager##*/}"
    echo "Graphviz has been installed successfully."

    # Add Graphviz to PATH
    if [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
        echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
        echo 'export PATH=$PATH:/usr/local/bin' >> ~/.zshrc
        echo "Graphviz executables have been added to your PATH. Please restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc) for the changes to take effect."
    else
        echo "Graphviz executables should already be in your PATH."
    fi
}

# Main script execution
install_ripgrep
install_graphviz

# Install system dependencies for pyaudio
sudo apt-get install -y clang
sudo apt-get install -y portaudio19-dev

# Install Python packages using rye
rye install pyaudio
rye install SpeechRecognition

echo "Setup completed successfully. Google Cloud credentials are configured."
