#!/bin/bash

# Terminator Snipbox Plugin Installer
# Provides automated installation and configuration

set -e

PLUGIN_DIR="$HOME/.config/terminator/plugins"
CONFIG_FILE="$HOME/.config/terminator/config"
PLUGIN_FILE="snipbox.py"
SNIPPETS_CONFIG="$HOME/.config/terminator/snippets.json"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if snippets.py exists
if [ ! -f "$PLUGIN_FILE" ]; then
    print_error "$PLUGIN_FILE not found in current directory"
    exit 1
fi

# Create plugins directory if it doesn't exist
mkdir -p "$PLUGIN_DIR"
print_success "Plugins directory ready"

# Copy plugin file
echo "Installing plugin to $PLUGIN_DIR..."
cp "$PLUGIN_FILE" "$PLUGIN_DIR/"
print_success "Plugin file installed"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    print_warning "Terminator config file not found at $CONFIG_FILE"
    print_info "Please create your Terminator config first by running 'terminator'"
    print_info "Then run this installer again"
    exit 0
fi

# Validate config file format
if ! grep -q "^\[global_config\]" "$CONFIG_FILE"; then
    print_error "Invalid Terminator config format"
    exit 1
fi

# Check if SnipBox plugin is already enabled
if grep -q "enabled_plugins.*SnipBoxPlugin" "$CONFIG_FILE"; then
    print_success "SnipBoxPlugin is already enabled in config"
else
    print_info "Adding SnipBoxPlugin to enabled_plugins in config..."

    # Backup config file
    cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
    print_success "Backup created at $CONFIG_FILE.bak"

    # Add SnipBoxPlugin to enabled_plugins
    if grep -q "^\s*enabled_plugins" "$CONFIG_FILE"; then
        # Plugin line already exists, append SnipBoxPlugin
        sed -i 's/^\(\s*enabled_plugins\s*=\s*[^#]*\)/\1SnipBoxPlugin, /' "$CONFIG_FILE"
        # Clean up any duplicate commas
        sed -i 's/,\s*,/,/g' "$CONFIG_FILE"
        sed -i 's/,\s*$//' "$CONFIG_FILE"
        print_success "SnipBoxPlugin added to enabled_plugins"
    else
        # Plugin line doesn't exist, add it to global_config section
        sed -i '/^\[global_config\]/a\  enabled_plugins = SnipBoxPlugin' "$CONFIG_FILE"
        print_success "enabled_plugins line created with SnipBoxPlugin"
    fi
fi

# Create plugins configuration section if it doesn't exist
if ! grep -q "^\[plugins\]" "$CONFIG_FILE"; then
    echo "[plugins]" >> "$CONFIG_FILE"
    echo "  [[SnipBoxPlugin]]" >> "$CONFIG_FILE"
    print_success "Plugin configuration section created"
fi

# Create default snippets config if it doesn't exist
if [ ! -f "$SNIPPETS_CONFIG" ]; then
    echo ""
    print_info "Snippets configuration not found"
    echo "Would you like to:"
    echo "  1) Use example snippets (recommended for first-time users)"
    echo "  2) Start with an empty configuration"
    echo ""
    read -p "Choose option (1 or 2): " choice

    case "$choice" in
        1)
            print_info "Using example snippets..."
            if [ -f "snippets.example.json" ]; then
                cp snippets.example.json "$SNIPPETS_CONFIG"
                print_success "Example snippets installed"
            else
                print_warning "snippets.example.json not found, creating default snippets instead..."
                python3 << 'EOF'
import os
import json

config_path = os.path.expanduser('~/.config/terminator/snippets.json')
default_snippets = {
    "Examples": {
        "list directory": "ls -la",
        "clear screen": "clear",
        "check ip": "ip addr show"
    }
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(default_snippets, f, indent=2, ensure_ascii=False)
EOF
                print_success "Default snippets created"
            fi
            ;;
        2)
            print_info "Creating empty snippets configuration..."
            python3 << 'EOF'
import os
import json

config_path = os.path.expanduser('~/.config/terminator/snippets.json')
empty_snippets = {}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(empty_snippets, f, indent=2, ensure_ascii=False)
EOF
            print_success "Empty snippets configuration created"
            ;;
        *)
            print_warning "Invalid option, using example snippets..."
            if [ -f "snippets.example.json" ]; then
                cp snippets.example.json "$SNIPPETS_CONFIG"
                print_success "Example snippets installed"
            else
                python3 << 'EOF'
import os
import json

config_path = os.path.expanduser('~/.config/terminator/snippets.json')
default_snippets = {
    "Examples": {
        "list directory": "ls -la",
        "clear screen": "clear",
        "check ip": "ip addr show"
    }
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(default_snippets, f, indent=2, ensure_ascii=False)
EOF
                print_success "Default snippets created"
            fi
            ;;
    esac
else
    print_success "Snippets configuration already exists"
fi

echo ""
echo "=========================================="
print_success "Installation Complete!"
echo "=========================================="
echo ""
print_info "Next steps:"
echo "  1. Close all Terminator windows"
echo "  2. Reopen Terminator"
echo "  3. Right-click in a terminal and select 'Manage Snippets'"
echo ""
print_info "To uninstall:"
echo "  rm $PLUGIN_DIR/$PLUGIN_FILE"
echo "  # Then remove 'SnipBoxPlugin' from enabled_plugins in your config"
echo ""
