"""Utilities for scraping news articles from the web."""

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime, timedelta

class NewsScraper:
    def __init__(self):
        """Initialize the news scraper."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_economic_news(self):
        """Scrape economic news related to tariffs, exchange rates, etc."""
        economic_news = []
        
        # Sources for economic news
        sources = [
            {"url": "https://www.reuters.com/business/", "domain": "reuters.com"},
            {"url": "https://www.ft.com/global-economy", "domain": "ft.com"},
            {"url": "https://www.bloomberg.com/markets", "domain": "bloomberg.com"}
        ]
        
        for source in sources:
            try:
                response = requests.get(source["url"], headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract headlines and links (implementation varies by website)
                    headlines = soup.find_all(['h2', 'h3', 'h4'])
                    
                    for headline in headlines:
                        if headline.text and len(headline.text.strip()) > 10:
                            link = None
                            if headline.find('a'):
                                link = headline.find('a').get('href')
                                if link and not link.startswith('http'):
                                    link = f"https://{source['domain']}{link}"
                            
                            economic_news.append({
                                "title": headline.text.strip(),
                                "source": source["domain"],
                                "link": link,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                            
            except Exception as e:
                print(f"Error scraping {source['url']}: {e}")
                
            # Respect rate limits
            time.sleep(2)
            
        return economic_news
        
    def get_geopolitical_news(self):
        """Scrape geopolitical news related to conflicts, trade restrictions, etc."""
        geopolitical_news = []
        
        # Sources for geopolitical news
        sources = [
            {"url": "https://www.aljazeera.com/middle-east/", "domain": "aljazeera.com"},
            {"url": "https://www.bbc.com/news/world", "domain": "bbc.com"},
            {"url": "https://www.cnn.com/world", "domain": "cnn.com"}
        ]
        
        for source in sources:
            try:
                response = requests.get(source["url"], headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract headlines and links
                    headlines = soup.find_all(['h2', 'h3', 'h4'])
                    
                    for headline in headlines:
                        if headline.text and len(headline.text.strip()) > 10:
                            link = None
                            if headline.find('a'):
                                link = headline.find('a').get('href')
                                if link and not link.startswith('http'):
                                    link = f"https://{source['domain']}{link}"
                            
                            geopolitical_news.append({
                                "title": headline.text.strip(),
                                "source": source["domain"],
                                "link": link,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                            
            except Exception as e:
                print(f"Error scraping {source['url']}: {e}")
                
            # Respect rate limits
            time.sleep(2)
            
        return geopolitical_news
        
    def filter_relevant_news(self, news_list, keywords):
        """Filter news articles based on relevant keywords."""
        relevant_news = []
        
        for news in news_list:
            if any(keyword.lower() in news["title"].lower() for keyword in keywords):
                relevant_news.append(news)
                
        return relevant_news