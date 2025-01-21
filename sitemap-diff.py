import os
import requests
import gzip
import xml.etree.ElementTree as ET
from difflib import unified_diff
import time

# Configuration
LOCAL_SITEMAP = 'sitemap.xml'  # Local uncompressed sitemap file
LOCAL_SITEMAP_GZ = 'sitemap.xml.gz'  # Local compressed sitemap file
CHECK_INTERVAL = 60  # Time in seconds between checks

def download_sitemap(sitemap_url):
    """Download the sitemap and save it locally."""
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        with open(LOCAL_SITEMAP_GZ, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download sitemap. Status code: {response.status_code}")

def extract_sitemap():
    """Extract the sitemap from the gzipped file."""
    with gzip.open(LOCAL_SITEMAP_GZ, 'rb') as f:
        with open(LOCAL_SITEMAP, 'wb') as out_f:
            out_f.write(f.read())

def parse_sitemap():
    """Parse the sitemap XML and return a list of URLs."""
    tree = ET.parse(LOCAL_SITEMAP)
    root = tree.getroot()
    
    # Assuming the sitemap follows the standard XML structure
    urls = [url_elem.text for url_elem in root.findall('{http://www.sitemaps.org/schemas/sitemap-image/1.1}loc')]
    return urls

def compare_sitemaps(old_urls, new_urls):
    """Compare two lists of URLs and print the differences."""
    diff = list(unified_diff(old_urls, new_urls, lineterm='', fromfile='old_sitemap', tofile='new_sitemap'))
    
    if diff:
        print("Differences found:")
        for line in diff:
            print(line)
    else:
        print("No differences found.")

def main():
    """Main function to monitor the sitemap."""
    sitemap_url = input("Enter the sitemap URL: ")
    previous_urls = []

    while True:
        download_sitemap(sitemap_url)
        extract_sitemap()
        current_urls = parse_sitemap()

        if previous_urls:
            compare_sitemaps(previous_urls, current_urls)

        previous_urls = current_urls
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()