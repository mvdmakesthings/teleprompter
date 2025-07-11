#!/bin/bash
# Build script for CueBird on macOS
# Creates a signed .app bundle and .dmg installer

set -e  # Exit on error

echo "🚀 Building CueBird for macOS..."

# Configuration
APP_NAME="CueBird"
VERSION="0.1.0"
BUNDLE_ID="com.cuebird.teleprompter"
BUILD_DIR="dist"
DMG_DIR="dmg_temp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Not in a virtual environment. Activating Poetry environment..."
    eval "$(poetry env info --path)/bin/activate"
fi

# Install dependencies
print_status "Installing dependencies..."
poetry install

# Create entitlements file for microphone access
print_status "Creating entitlements.plist..."
cat > entitlements.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.device.audio-input</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
</dict>
</plist>
EOF

# Build the application
print_status "Building application with PyInstaller..."
poetry run pyinstaller cuebird.spec --clean --noconfirm

# Check if build was successful
if [ ! -d "dist/${APP_NAME}.app" ]; then
    print_error "Build failed! ${APP_NAME}.app not found in dist/"
    exit 1
fi

print_status "Build successful! ${APP_NAME}.app created."

# Code signing (optional - requires Apple Developer certificate)
if command -v codesign &> /dev/null; then
    print_status "Checking for code signing certificate..."
    
    # Try to find a valid Developer ID certificate
    CERT=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | awk -F'"' '{print $2}')
    
    if [ ! -z "$CERT" ]; then
        print_status "Found certificate: $CERT"
        print_status "Signing application..."
        
        # Sign the app bundle
        codesign --deep --force --verbose --sign "$CERT" \
            --entitlements entitlements.plist \
            --options runtime \
            "dist/${APP_NAME}.app"
        
        # Verify the signature
        codesign --verify --deep --strict --verbose=2 "dist/${APP_NAME}.app"
        
        print_status "Application signed successfully!"
    else
        print_warning "No Developer ID certificate found. App will not be signed."
        print_warning "Users may see security warnings when running the app."
    fi
else
    print_warning "codesign not found. Skipping code signing."
fi

# Create DMG installer
print_status "Creating DMG installer..."

# Clean up any existing DMG temp directory
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copy app to DMG directory
cp -R "dist/${APP_NAME}.app" "$DMG_DIR/"

# Create a symbolic link to Applications folder
ln -s /Applications "$DMG_DIR/Applications"

# Create DMG
DMG_NAME="${APP_NAME}-${VERSION}-macOS.dmg"
hdiutil create -volname "$APP_NAME" \
    -srcfolder "$DMG_DIR" \
    -ov -format UDZO \
    "$BUILD_DIR/$DMG_NAME"

# Clean up
rm -rf "$DMG_DIR"
rm -f entitlements.plist

# Create a simple install instructions file
cat > "dist/INSTALL_INSTRUCTIONS.txt" << EOF
CueBird Installation Instructions for macOS
==========================================

1. Open the ${DMG_NAME} file
2. Drag the ${APP_NAME} icon to the Applications folder
3. Close the DMG window
4. Launch ${APP_NAME} from your Applications folder

First Launch:
- You may see a security warning. This is normal for apps not from the App Store.
- Right-click on ${APP_NAME} and select "Open" to bypass the warning.
- Grant microphone access when prompted for voice control features.

System Requirements:
- macOS 10.13 (High Sierra) or later
- 64-bit processor
- 4GB RAM recommended

Troubleshooting:
- If the app doesn't open, check System Preferences > Security & Privacy
- For microphone issues, check System Preferences > Security & Privacy > Microphone

Enjoy using CueBird!
EOF

print_status "Build complete!"
echo ""
echo "📦 Application: dist/${APP_NAME}.app"
echo "💿 Installer: dist/$DMG_NAME"
echo "📝 Instructions: dist/INSTALL_INSTRUCTIONS.txt"
echo ""
print_status "Next steps:"
echo "  1. Test the application: open dist/${APP_NAME}.app"
echo "  2. Distribute the DMG file to users"
echo ""

# Optional: Open the dist folder
if command -v open &> /dev/null; then
    open dist/
fi