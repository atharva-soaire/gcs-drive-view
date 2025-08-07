#!/bin/bash

echo "🖼️  Setting up GCS Image Gallery Generator..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set up Google Cloud authentication (see README.md)"
echo "3. Run the gallery generator"
echo ""
echo "💡 Example usage:"
echo "python gcs_gallery_generator.py --project central-database-454408 --bucket copied-wms-image-store --folder WMS_V4/2C-CF-67-ED-B1-62"