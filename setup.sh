#!/bin/bash

# This script sets up the environment for the AI Playground project.
# It installs necessary dependencies, configures Google Cloud credentials, and fetches the dataset.

# Install portaudio19-dev if not already installed to ensure pyaudio can build
if ! dpkg -s portaudio19-dev >/dev/null 2>&1; then
    echo "Installing portaudio19-dev..."
    sudo apt-get install -y portaudio19-dev
else
    echo "portaudio19-dev is already installed."
fi

# Add check for rye installation and install if not present
if ! command -v rye &> /dev/null; then
    echo "Rye is not installed. Installing Rye..."
    curl -fsSL https://raw.githubusercontent.com/rye/rye/main/install.sh | bash
else
    echo "Rye is already installed."
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

fetch_dataset() {
    # URL of the dataset
    DATASET_URL="https://huggingface.co/datasets/THUDM/humaneval-x/viewer"

    # Output file
    OUTPUT_FILE="human_eval_problems.json"

    # Fetch the dataset
    echo "Fetching dataset from $DATASET_URL..."
    if command -v curl &> /dev/null; then
        curl -s "$DATASET_URL" | jq '.' > "$OUTPUT_FILE"
    elif command -v wget &> /dev/null; then
        wget -qO- "$DATASET_URL" | jq '.' > "$OUTPUT_FILE"
    else
        echo "Error: Neither curl nor wget is available. Please install one of them to fetch the dataset."
        return 1
    fi

    # Check if the fetch was successful
    if [ $? -eq 0 ]; then
        echo "Dataset successfully fetched and saved to $OUTPUT_FILE"
    else
        echo "Error: Failed to fetch the dataset"
        return 1
    fi
}

# Main script execution
install_ripgrep
install_graphviz
fetch_dataset

# Make the script executable
chmod +x "$0"
