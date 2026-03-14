"""ArXiv Paper Fetcher with Rate Limiting and Retry Logic"""

import requests
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Rate limiting configuration
ARXIV_BASE_URL = "https://export.arxiv.org/api/query"
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds
MIN_REQUEST_INTERVAL = 3  # seconds between requests


class ArxivFetcher:
    """Handles ArXiv API requests with rate limiting and retry logic"""
    
    def __init__(self):
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _wait_for_rate_limit(self):
        """Enforce minimum time between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - elapsed
            logger.info(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse ArXiv XML response"""
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                try:
                    # Extract paper information
                    title = entry.findtext('atom:title', '', ns).strip()
                    arxiv_id = entry.findtext('atom:id', '', ns).split('/abs/')[-1] if 'arxiv.org' in entry.findtext('atom:id', '', ns) else ''
                    published = entry.findtext('atom:published', '', ns)
                    summary = entry.findtext('atom:summary', '', ns).strip()
                    
                    # Extract authors
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        author_name = author.findtext('atom:name', '', ns)
                        if author_name:
                            authors.append(author_name)
                    
                    # Extract year from published date
                    year = published[:4] if published else 'Unknown'
                    
                    # Extract URL
                    url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'published': published,
                        'year': year,
                        'summary': summary,
                        'arxiv_id': arxiv_id,
                        'url': url,
                        'source': 'ArXiv'
                    }
                    
                    if title:  # Only add if has title
                        papers.append(paper)
                
                except Exception as e:
                    logger.warning(f"Error parsing entry: {e}")
                    continue
            
            return papers
        
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing ArXiv response: {e}")
            return []
    
    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch papers from ArXiv with retry logic
        
        Args:
            query: Search query string
            max_results: Maximum number of results to fetch
            
        Returns:
            List of paper dictionaries
        """
        
        # Enforce rate limiting
        self._wait_for_rate_limit()
        
        # Prepare request parameters
        search_query = f"all:{query}"
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': min(max_results, 100),  # ArXiv limit is 100 per request
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        # Retry logic
        for attempt in range(RETRY_ATTEMPTS):
            try:
                logger.info(f"Fetching from ArXiv (attempt {attempt + 1}/{RETRY_ATTEMPTS}): {query}")
                
                response = self.session.get(
                    ARXIV_BASE_URL,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )
                
                self.last_request_time = time.time()
                
                # Check for rate limiting (429) or other errors
                if response.status_code == 429:
                    if attempt < RETRY_ATTEMPTS - 1:
                        wait_time = RETRY_DELAY * (attempt + 1)
                        logger.warning(f"Rate limited (429). Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limited after all retries")
                
                elif response.status_code == 200:
                    papers = self._parse_arxiv_response(response.text)
                    logger.info(f"Successfully fetched {len(papers)} papers")
                    return papers
                
                elif response.status_code == 400:
                    logger.error("Bad request - check query syntax")
                    return []
                
                elif response.status_code == 403:
                    logger.error("Forbidden - access denied")
                    return []
                
                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    if attempt < RETRY_ATTEMPTS - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        return []
            
            except requests.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{RETRY_ATTEMPTS})")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    raise Exception("Request timeout after all retries")
            
            except requests.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1}/{RETRY_ATTEMPTS})")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    raise Exception("Connection error after all retries")
            
            except Exception as e:
                logger.error(f"Error fetching papers: {e}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    raise
        
        return []


def get_sample_papers() -> List[Dict]:
    """Return sample papers for testing/offline mode"""
    return [
        {
            'title': 'Attention Is All You Need',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Parmar N.', 'Jakob Uszkoreit'],
            'published': '2017-06-12',
            'year': '2017',
            'summary': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism.',
            'arxiv_id': '1706.03762',
            'url': 'https://arxiv.org/abs/1706.03762',
            'source': 'ArXiv'
        },
        {
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
            'authors': ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee', 'Kristina Toutanova'],
            'published': '2018-10-11',
            'year': '2018',
            'summary': 'We introduce BERT, a new method of pre-training language representations. BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.',
            'arxiv_id': '1810.04805',
            'url': 'https://arxiv.org/abs/1810.04805',
            'source': 'ArXiv'
        },
        {
            'title': 'Language Models are Unsupervised Multitask Learners',
            'authors': ['Alec Radford', 'Jeffrey Wu', 'Rewon Child', 'David Luan'],
            'published': '2019-02-14',
            'year': '2019',
            'summary': 'Natural language processing tasks are typically approached with supervised learning on task-specific datasets. We demonstrate that language models begin to learn these tasks without any explicit supervision when trained on a new dataset of Internet text carefully filtered to match the characteristics of datasets used in prior work on supervised learning.',
            'arxiv_id': '1901.11990',
            'url': 'https://arxiv.org/abs/1901.11990',
            'source': 'ArXiv'
        },
        {
            'title': 'An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale',
            'authors': ['Alexey Dosovitskiy', 'Lucas Beyer', 'Alexander Kolesnikov', 'Dirk Weissenborn'],
            'published': '2020-10-22',
            'year': '2020',
            'summary': 'While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. In vision, attention is either applied in conjunction with convolutional networks, or used to replace certain components of convolutional networks while keeping their overall structure in place.',
            'arxiv_id': '2010.11929',
            'url': 'https://arxiv.org/abs/2010.11929',
            'source': 'ArXiv'
        },
        {
            'title': 'Flamingo: a Visual Language Model for Few-Shot Learning',
            'authors': ['Jean-Baptiste Alayrac', 'Jeff Donahue', 'Pauline Luc', 'Antoine Miech'],
            'published': '2022-04-29',
            'year': '2022',
            'summary': 'Building and releasing large-scale vision-language models is challenging, but is of high importance for research which aims to make multimodal systems more widely available. We present Flamingo, a family of visual language models with strong few-shot learning capabilities.',
            'arxiv_id': '2204.14198',
            'url': 'https://arxiv.org/abs/2204.14198',
            'source': 'ArXiv'
        }
    ]


# Global fetcher instance
_fetcher = None

def get_fetcher() -> ArxivFetcher:
    """Get or create ArXiv fetcher instance"""
    global _fetcher
    if _fetcher is None:
        _fetcher = ArxivFetcher()
    return _fetcher


def fetch_papers(query: str, max_results: int = 10, use_sample: bool = False) -> tuple:
    """
    Fetch papers from ArXiv with fallback to sample data
    
    Args:
        query: Search query
        max_results: Number of papers to fetch
        use_sample: Force use of sample data
        
    Returns:
        Tuple of (papers_list, success_bool, message_str)
    """
    
    if use_sample:
        return get_sample_papers(), True, "Using sample papers (demo mode)"
    
    try:
        fetcher = get_fetcher()
        papers = fetcher.fetch_papers(query, max_results)
        
        if papers:
            return papers, True, f"Successfully fetched {len(papers)} papers from ArXiv"
        else:
            logger.info("No papers found, using sample papers")
            return get_sample_papers(), True, "No papers found on ArXiv. Showing sample papers instead."
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to fetch papers: {error_msg}")
        
        # Return sample papers as fallback
        return get_sample_papers(), False, f"Failed to fetch from ArXiv ({error_msg}). Using sample papers instead."