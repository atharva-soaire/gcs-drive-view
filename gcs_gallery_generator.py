#!/usr/bin/env python3
"""
GCS Image Gallery Generator

This script fetches images from a Google Cloud Storage bucket,
sorts them by image name, and generates a paginated HTML gallery with date filtering.
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.cloud import storage
from jinja2 import Template
import argparse
import sys
from collections import defaultdict

class GCSImageGallery:
    def __init__(self, project_id: str, bucket_name: str, folder_path: str = ""):
        """
        Initialize the GCS Image Gallery generator.
        
        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name
            folder_path: Folder path within the bucket (optional)
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.folder_path = folder_path.rstrip('/') + '/' if folder_path else ""
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)
        
    def get_image_list(self) -> List[Dict]:
        """
        Fetch all images from the GCS bucket with metadata.
        
        Returns:
            List of dictionaries containing image metadata
        """
        print(f"Fetching images from gs://{self.bucket_name}/{self.folder_path}...")
        
        # Common image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}
        
        images = []
        blobs = self.bucket.list_blobs(prefix=self.folder_path)
        
        count = 0
        for blob in blobs:
            # Check if it's an image file
            if any(blob.name.lower().endswith(ext) for ext in image_extensions):
                # Get blob metadata
                blob.reload()  # Ensure we have fresh metadata
                
                # Extract date from filename (format: DT20250801_...)
                filename = os.path.basename(blob.name)
                date_match = re.search(r'DT(\d{8})', filename)
                date_str = None
                if date_match:
                    date_str = date_match.group(1)
                    # Convert YYYYMMDD to readable format
                    try:
                        date_obj = datetime.strptime(date_str, '%Y%m%d')
                        date_display = date_obj.strftime('%d %B')  # e.g., "01 August"
                    except:
                        date_display = date_str
                else:
                    date_display = "Unknown Date"
                
                # Generate signed URL that works for private buckets
                try:
                    # Try to generate a signed URL (valid for 1 hour)
                    signed_url = blob.generate_signed_url(
                        expiration=datetime.now() + timedelta(hours=1),
                        method='GET'
                    )
                except Exception as e:
                    # Fallback to public URL if signing fails
                    if count <= 5:  # Only print first few errors to avoid spam
                        print(f"Warning: Could not generate signed URL for {filename}: {e}")
                        print("Falling back to public URL format...")
                    signed_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}"
                
                image_info = {
                    'name': blob.name,
                    'filename': filename,
                    'public_url': signed_url,
                    'size': blob.size,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'content_type': blob.content_type,
                    'md5_hash': blob.md5_hash,
                    'date_str': date_str,
                    'date_display': date_display
                }
                
                images.append(image_info)
                count += 1
                
                if count % 1000 == 0:
                    print(f"Processed {count} images...")
        
        print(f"Found {len(images)} images total.")
        
        # Sort by image name (alphabetical)
        images.sort(key=lambda x: x['filename'])
        
        return images
    
    def generate_html_gallery(self, images: List[Dict], 
                            output_file: str = "gallery.html",
                            images_per_page: int = 250,
                            title: str = "GCS Image Gallery") -> None:
        """
        Generate HTML gallery with pagination.
        
        Args:
            images: List of image metadata
            output_file: Output HTML file name
            images_per_page: Number of images per page
            title: Gallery title
        """
        print(f"Generating HTML gallery with {len(images)} images...")
        
        # Calculate total pages
        total_pages = (len(images) + images_per_page - 1) // images_per_page
        
        html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .controls {
            background: white;
            padding: 1rem;
            margin: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .search-box {
            display: flex;
            align-items: center;
            gap: 1rem;
            flex: 1;
            min-width: 200px;
        }
        
        .search-box input, .search-box select {
            padding: 0.5rem;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
            background: white;
        }
        
        .search-box input {
            flex: 1;
            max-width: 300px;
        }
        
        .search-box select {
            min-width: 150px;
        }
        
        .pagination {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .pagination button {
            padding: 0.5rem 1rem;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }
        
        .pagination button:hover:not(:disabled) {
            background: #667eea;
            color: white;
        }
        
        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .pagination .current-page {
            background: #667eea;
            color: white;
        }
        
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
            padding: 1rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .image-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .image-container {
            position: relative;
            width: 100%;
            height: 200px;
            overflow: hidden;
            background: #f0f0f0;
        }
        
        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
            cursor: pointer;
            background: #f0f0f0;
        }
        
        .image-container img.loading {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            min-height: 150px;
        }
        
        .image-container img.loaded {
            opacity: 1;
            transition: opacity 0.3s ease;
        }
        
        @keyframes loading {
            0% {
                background-position: 200% 0;
            }
            100% {
                background-position: -200% 0;
            }
        }
        
        .fast-loading {
            will-change: transform;
        }
        
        .image-container:hover img {
            transform: scale(1.05);
        }
        
        .image-info {
            padding: 1rem;
        }
        
        .image-title {
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            word-break: break-word;
        }
        
        .image-meta {
            font-size: 0.8rem;
            color: #666;
            line-height: 1.4;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            font-size: 1.1rem;
            color: #666;
        }
        
        .no-results {
            text-align: center;
            padding: 3rem;
            color: #666;
            font-size: 1.2rem;
        }
        
        /* Modal for full-size images */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }
        
        .modal-content {
            position: relative;
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            top: 50%;
            transform: translateY(-50%);
        }
        
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #bbb;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-box {
                flex-direction: column;
                align-items: stretch;
            }
            
            .gallery {
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p>{{ total_images }} images sorted by name ({{ images_per_page }} per page for fast loading)</p>
    </div>
    
    <div class="controls">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search images by filename..." onkeyup="filterImages()">
            <select id="dateFilter" onchange="filterImages()">
                <option value="">All Dates</option>
            </select>
            <span id="resultCount">Showing {{ images_per_page }} of {{ total_images }}</span>
        </div>
        <div class="pagination">
            <button onclick="changePage(-1)" id="prevBtn">← Previous</button>
            <span id="pageInfo">Page <span id="currentPage">1</span> of <span id="totalPages">{{ total_pages }}</span></span>
            <button onclick="changePage(1)" id="nextBtn">Next →</button>
        </div>
    </div>
    
    <div id="gallery" class="gallery">
        <!-- Images will be loaded here -->
    </div>
    
    <div class="loading" id="loading" style="display: none;">
        Loading images...
    </div>
    
    <div class="no-results" id="noResults" style="display: none;">
        No images found matching your search.
    </div>
    
    <!-- Modal for full-size images -->
    <div id="imageModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        // Image data embedded in the HTML
        const imageData = {{ images_json|safe }};
        const imagesPerPage = {{ images_per_page }};
        let currentPage = 1;
        let filteredImages = imageData;
        
        function displayImages(images, page = 1) {
            const gallery = document.getElementById('gallery');
            const startIndex = (page - 1) * imagesPerPage;
            const endIndex = startIndex + imagesPerPage;
            const pageImages = images.slice(startIndex, endIndex);
            
            gallery.innerHTML = '';
            
            if (pageImages.length === 0) {
                document.getElementById('noResults').style.display = 'block';
                return;
            }
            
            document.getElementById('noResults').style.display = 'none';
            
            pageImages.forEach(image => {
                const card = document.createElement('div');
                card.className = 'image-card';
                
                const sizeKB = Math.round(image.size / 1024);
                
                card.innerHTML = `
                    <div class="image-container">
                        <img data-src="${image.public_url}" alt="${image.filename}" 
                             class="lazy-image loading" 
                             onclick="openModal('${image.public_url}')"
                             loading="lazy"
                             decoding="async"
                             onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=\\"display:flex;align-items:center;justify-content:center;height:100%;background:#f0f0f0;color:#666;\\">Image not available</div>'">
                    </div>
                    <div class="image-info">
                        <div class="image-title">${image.filename}</div>
                        <div class="image-meta">
                            Date: ${image.date_display}<br>
                            Size: ${sizeKB} KB<br>
                            Type: ${image.content_type}
                        </div>
                    </div>
                `;
                
                gallery.appendChild(card);
            });
            
            updatePagination(images.length, page);
            updateResultCount(images.length, page);
            
            // Re-observe new images for lazy loading
            setTimeout(() => {
                observeImages();
            }, 100);
        }
        
        function updatePagination(totalItems, page) {
            const totalPages = Math.ceil(totalItems / imagesPerPage);
            document.getElementById('currentPage').textContent = page;
            document.getElementById('totalPages').textContent = totalPages;
            document.getElementById('prevBtn').disabled = page <= 1;
            document.getElementById('nextBtn').disabled = page >= totalPages;
        }
        
        function updateResultCount(totalItems, page) {
            const startIndex = (page - 1) * imagesPerPage + 1;
            const endIndex = Math.min(page * imagesPerPage, totalItems);
            document.getElementById('resultCount').textContent = 
                `Showing ${startIndex}-${endIndex} of ${totalItems}`;
        }
        
        function changePage(direction) {
            const totalPages = Math.ceil(filteredImages.length / imagesPerPage);
            const newPage = currentPage + direction;
            
            if (newPage >= 1 && newPage <= totalPages) {
                currentPage = newPage;
                displayImages(filteredImages, currentPage);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
        
        function filterImages() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const dateFilter = document.getElementById('dateFilter').value;
            
            filteredImages = imageData.filter(image => {
                const matchesSearch = image.filename.toLowerCase().includes(searchTerm);
                const matchesDate = dateFilter === '' || image.date_str === dateFilter;
                return matchesSearch && matchesDate;
            });
            
            currentPage = 1;
            displayImages(filteredImages, currentPage);
        }
        
        function populateDateFilter() {
            const dateFilter = document.getElementById('dateFilter');
            const uniqueDates = [...new Set(imageData.map(img => img.date_str).filter(date => date))];
            
            // Sort dates
            uniqueDates.sort();
            
            uniqueDates.forEach(dateStr => {
                const option = document.createElement('option');
                option.value = dateStr;
                
                // Convert YYYYMMDD to readable format
                try {
                    const date = new Date(dateStr.substring(0,4), 
                                         parseInt(dateStr.substring(4,6)) - 1, 
                                         dateStr.substring(6,8));
                    option.textContent = date.toLocaleDateString('en-GB', { 
                        day: 'numeric', 
                        month: 'long' 
                    });
                } catch {
                    option.textContent = dateStr;
                }
                
                dateFilter.appendChild(option);
            });
        }
        
        function openModal(imageUrl) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImg.src = imageUrl;
        }
        
        // Close modal
        document.querySelector('.close').onclick = function() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        window.onclick = function(event) {
            const modal = document.getElementById('imageModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
        
        // Intersection Observer for lazy loading
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('loading');
                    img.onload = () => {
                        img.classList.add('loaded');
                    };
                    observer.unobserve(img);
                }
            });
        }, {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        });
        
        function observeImages() {
            const lazyImages = document.querySelectorAll('.lazy-image');
            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Initialize the gallery
        populateDateFilter();
        displayImages(imageData, 1);
        
        // Observe images after they're added to DOM
        setTimeout(() => {
            observeImages();
        }, 100);
    </script>
</body>
</html>
        '''
        
        template = Template(html_template)
        
        # Prepare images data for JavaScript (limit what we include to save file size)
        images_for_js = []
        for img in images:
            # Ensure URL is properly escaped for JSON
            public_url = img['public_url']
            if public_url:
                # Escape any backslashes and quotes that might break JSON
                public_url = public_url.replace('\\', '\\\\').replace('"', '\\"')
            
            images_for_js.append({
                'filename': img['filename'].replace('\\', '\\\\').replace('"', '\\"') if img['filename'] else '',
                'public_url': public_url or '',
                'size': img['size'],
                'created': img['created'].isoformat() if img['created'] else None,
                'content_type': img['content_type'] or 'image/unknown',
                'date_str': img['date_str'] or '',
                'date_display': img['date_display'] or 'Unknown Date'
            })
        
        html_content = template.render(
            title=title,
            total_images=len(images),
            images_per_page=images_per_page,
            total_pages=total_pages,
            images_json=json.dumps(images_for_js)
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Gallery generated successfully: {output_file}")
        print(f"Total images: {len(images)}")
        print(f"Pages: {total_pages}")

def main():
    parser = argparse.ArgumentParser(description='Generate HTML gallery from GCS bucket images')
    parser.add_argument('--project', required=True, help='GCP project ID')
    parser.add_argument('--bucket', required=True, help='GCS bucket name')
    parser.add_argument('--folder', default='', help='Folder path within bucket')
    parser.add_argument('--output', default='gallery.html', help='Output HTML file name')
    parser.add_argument('--per-page', type=int, default=250, help='Images per page')
    parser.add_argument('--title', default='GCS Image Gallery', help='Gallery title')
    
    args = parser.parse_args()
    
    try:
        # Initialize gallery generator
        gallery = GCSImageGallery(args.project, args.bucket, args.folder)
        
        # Fetch images
        images = gallery.get_image_list()
        
        if not images:
            print("No images found in the specified bucket/folder.")
            sys.exit(1)
        
        # Generate HTML gallery
        gallery.generate_html_gallery(
            images, 
            args.output, 
            args.per_page, 
            args.title
        )
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()