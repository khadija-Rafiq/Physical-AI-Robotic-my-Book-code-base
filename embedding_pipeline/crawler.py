"""
Docusaurus Crawler Module
Handles crawling and text extraction from Docusaurus documentation sites
"""
import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import List, Dict
import time
import logging

logger = logging.getLogger(__name__)

class DocusaurusCrawler:
    def __init__(self, delay: float = 1.0):
        """
        Initialize the Docusaurus crawler
        :param delay: Delay between requests in seconds to be respectful to the server
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; DocusaurusCrawler/1.0; +https://github.com/example)'
        })

    def extract_text_from_url(self, url: str) -> str:
        """
        Extract text content from a single URL
        :param url: URL to extract text from
        :return: Extracted text content
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Focus on main content areas typical in Docusaurus sites
            # Look for main content containers
            content_selectors = [
                'article',  # Main article content
                '.markdown',  # Markdown content
                '.theme-doc-markdown',  # Docusaurus-specific class
                '.docItemContainer',  # Docusaurus document container
                'main',  # Main content area
                '.container',  # Container divs
                '.row'  # Row divs often contain content
            ]

            text_parts = []

            # Try specific Docusaurus selectors first
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text_parts.append(element.get_text(separator=' ', strip=True))
                    break  # Take the first match to avoid duplication

            # If no specific content found, fall back to body
            if not text_parts:
                body = soup.find('body')
                if body:
                    text_parts.append(body.get_text(separator=' ', strip=True))

            # Combine all text parts
            full_text = ' '.join(text_parts)

            # Clean up excessive whitespace
            import re
            full_text = re.sub(r'\s+', ' ', full_text).strip()

            time.sleep(self.delay)  # Be respectful to the server
            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return ""

    def get_sitemap_urls(self, base_url: str) -> List[str]:
        """
        Extract URLs from a sitemap if available
        :param base_url: Base URL of the site
        :return: List of URLs from sitemap
        """
        sitemap_url = urllib.parse.urljoin(base_url, 'sitemap.xml')

        try:
            response = self.session.get(sitemap_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'xml')
            urls = []

            # Look for <url><loc> elements in sitemap
            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                if base_url in url:  # Only include URLs from the same domain
                    urls.append(url)

            return urls

        except Exception as e:
            logger.warning(f"Sitemap not found at {sitemap_url}: {str(e)}")
            # Fallback: try robots.txt for sitemap reference
            return self._get_sitemap_from_robots(base_url)

    def _get_sitemap_from_robots(self, base_url: str) -> List[str]:
        """
        Get sitemap URL from robots.txt
        :param base_url: Base URL of the site
        :return: List of URLs from sitemap
        """
        robots_url = urllib.parse.urljoin(base_url, 'robots.txt')

        try:
            response = self.session.get(robots_url)
            response.raise_for_status()

            sitemap_lines = [line for line in response.text.split('\n') if line.startswith('Sitemap:')]

            if sitemap_lines:
                sitemap_url = sitemap_lines[0].split(':', 1)[1].strip()
                return self._parse_sitemap(sitemap_url)

            return []

        except Exception as e:
            logger.warning(f"Could not get sitemap from robots.txt: {str(e)}")
            return []

    def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Parse a sitemap URL and return contained URLs
        :param sitemap_url: URL of the sitemap
        :return: List of URLs
        """
        try:
            response = self.session.get(sitemap_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'xml')
            urls = []

            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                urls.append(url)

            return urls

        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {str(e)}")
            return []

    def crawl_docusaurus_site(self, base_url: str, max_pages: int = 100) -> List[Dict[str, str]]:
        """
        Crawl an entire Docusaurus site to extract content
        :param base_url: Base URL of the Docusaurus site
        :param max_pages: Maximum number of pages to crawl
        :return: List of dictionaries containing URL and extracted text
        """
        # Get URLs from sitemap
        urls = self.get_sitemap_urls(base_url)

        if not urls:
            logger.info("No sitemap found, attempting manual discovery...")
            # If no sitemap, we could implement more advanced crawling here
            # For now, we'll return empty list
            logger.warning("Manual crawling not implemented yet, only sitemap URLs available")
            return []

        results = []
        for i, url in enumerate(urls[:max_pages]):
            logger.info(f"Crawling ({i+1}/{min(len(urls), max_pages)}): {url}")
            text = self.extract_text_from_url(url)

            if text:  # Only add if we got content
                results.append({
                    'url': url,
                    'text': text
                })

        return results