# GCS Image Gallery Generator

A Python tool to generate a beautiful, paginated HTML gallery from Google Cloud Storage bucket images, sorted by creation time.

## Features

- 🖼️ **Smart Image Detection**: Automatically detects image files by extension
- ⏰ **Time-based Sorting**: Sorts images by creation time (newest first)
- 📄 **Pagination**: Handles 25,000+ images with efficient pagination
- 🔍 **Search Functionality**: Real-time search by filename
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🖱️ **Modal Viewer**: Click to view full-size images
- ⚡ **Lazy Loading**: Optimized performance for large galleries

## Quick Start

### 1. Setup

```bash
# Clone or download the files
chmod +x setup.sh
./setup.sh
```

### 2. Google Cloud Authentication

You need to authenticate with Google Cloud. Choose one of these methods:

#### Option A: Service Account Key (Recommended for production)
1. Go to [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a service account with Storage Object Viewer role
3. Download the JSON key file
4. Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

#### Option B: User Account (Quick for testing)
```bash
# Install Google Cloud CLI if not already installed
# macOS:
brew install google-cloud-sdk

# Then authenticate:
gcloud auth application-default login
gcloud config set project central-database-454408
```

### 3. Generate Your Gallery

```bash
# Activate the virtual environment
source venv/bin/activate

# Generate gallery for your WMS_V4/2C-CF-67-ED-B1-62 folder
python gcs_gallery_generator.py \
    --project central-database-454408 \
    --bucket copied-wms-image-store \
    --folder WMS_V4/2C-CF-67-ED-B1-62 \
    --output my_image_gallery.html \
    --per-page 100 \
    --title "WMS V3 Image Gallery"
```

### 4. View Your Gallery

Open the generated HTML file in your browser:
```bash
open my_image_gallery.html  # macOS
# or
xdg-open my_image_gallery.html  # Linux
# or just double-click the file
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project` | GCP project ID | Required |
| `--bucket` | GCS bucket name | Required |
| `--folder` | Folder path within bucket | "" (root) |
| `--output` | Output HTML file name | gallery.html |
| `--per-page` | Images per page | 100 |
| `--title` | Gallery title | GCS Image Gallery |

## Examples

### Basic usage for your WMS_V4/2C-CF-67-ED-B1-62 folder:
```bash
python gcs_gallery_generator.py \
    --project central-database-454408 \
    --bucket copied-wms-image-store \
    --folder WMS_V4/2C-CF-67-ED-B1-62
```

### Custom settings for large galleries:
```bash
python gcs_gallery_generator.py \
    --project central-database-454408 \
    --bucket copied-wms-image-store \
    --folder WMS_V4/2C-CF-67-ED-B1-62 \
    --per-page 50 \
    --title "My 25K+ Image Collection" \
    --output large_gallery.html
```

### Multiple folders (run separately):
```bash
# Generate separate galleries for different folders
python gcs_gallery_generator.py --project central-database-454408 --bucket copied-wms-image-store --folder WMS_V4/2C-CF-67-ED-B1-62 --output wms_v4_gallery.html
python gcs_gallery_generator.py --project central-database-454408 --bucket copied-wms-image-store --folder WMS_V4/other-device --output wms_v4_other_gallery.html
```

## Gallery Features

### Navigation
- **Pagination**: Navigate through pages of images
- **Search**: Type to filter images by filename
- **Responsive**: Adapts to different screen sizes

### Image Viewing
- **Thumbnails**: Fast-loading preview images
- **Modal View**: Click any image to see full size
- **Metadata**: Shows creation date, file size, and type
- **Lazy Loading**: Images load as you scroll

### Performance Optimizations
- Images are loaded on-demand
- Metadata is embedded in HTML for fast filtering
- Efficient pagination for large datasets
- CSS Grid for responsive layouts

## Troubleshooting

### Authentication Issues
```bash
# Check your current authentication
gcloud auth list
gcloud config get-value project

# Re-authenticate if needed
gcloud auth application-default login
```

### Permission Issues
Make sure your account has these IAM roles:
- `Storage Object Viewer` (minimum)
- `Storage Legacy Bucket Reader` (if needed)

### Large Dataset Performance
For 25,000+ images:
- Use `--per-page 50` for faster page loads
- Consider generating multiple galleries by subfolder
- Ensure stable internet connection during metadata fetch

### No Images Found
- Check bucket and folder names are correct
- Verify images have proper extensions (.jpg, .png, etc.)
- Ensure bucket is accessible from your account

## Technical Details

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff)
- SVG (.svg)

### Performance Notes
- Fetching metadata for 25,000 images takes approximately 10-15 minutes
- Generated HTML file size: ~5-10MB for 25,000 images
- Gallery loads 100 images per page by default for optimal performance

### Browser Compatibility
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

## License

This project is open source and available under the MIT License.