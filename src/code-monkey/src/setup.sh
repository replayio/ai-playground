#!/bin/bash

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

# Main script execution
install_ripgrep