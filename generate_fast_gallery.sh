#!/bin/bash

# Fast gallery generation script with optimizations

echo "🚀 Generating Fast WMS V3 Image Gallery..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set up service account authentication
SERVICE_ACCOUNT_KEY="central-database-454408-2dc4b26eb929.json"

if [ -f "$SERVICE_ACCOUNT_KEY" ]; then
    echo "🔑 Using service account: $SERVICE_ACCOUNT_KEY"
    export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT_KEY"
else
    echo "❌ Service account key file not found: $SERVICE_ACCOUNT_KEY"
    echo "Please ensure the service account JSON file is in the current directory."
    echo ""
    echo "Expected file: $SERVICE_ACCOUNT_KEY"
    echo "Current directory: $(pwd)"
    echo ""
    exit 1
fi

# Verify Google Cloud authentication
if ! python -c "from google.cloud import storage; storage.Client()" 2>/dev/null; then
    echo "❌ Google Cloud authentication failed."
    echo "Please check that the service account key file is valid."
    exit 1
fi

# Generate the fast gallery
echo "🔄 Fetching images from WMS_V3/2C-CF-67-A6-C7-4E folder..."
echo "⚡ Using optimized settings: 250 images per page with lazy loading"
echo "🔐 Generating signed URLs for secure access to private bucket..."

python gcs_gallery_generator.py \
    --project central-database-454408 \
    --bucket wms-image-storage \
    --folder WMS_V3/2C-CF-67-A6-C7-4E \
    --output wms_v3_fast_gallery.html \
    --per-page 250 \
    --title "WMS V3 Fast Gallery - Optimized Loading"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Fast gallery generated successfully!"
    echo "📁 Output file: wms_v3_fast_gallery.html"
    echo "⚡ Optimizations applied:"
    echo "   • 250 images per page (instead of 1000)"
    echo "   • Intersection Observer lazy loading"
    echo "   • Progressive image loading"
    echo "   • Loading animations"
    echo "   • Optimized DOM rendering"
    echo "   • Signed URLs for private bucket access"
    echo ""
    echo "🌐 Open the file in your browser:"
    echo "  open wms_v3_fast_gallery.html  # macOS"
    echo "  xdg-open wms_v3_fast_gallery.html  # Linux"
    echo "  # Or double-click the file"
else
    echo "❌ Gallery generation failed. Check the error messages above."
    exit 1
fi