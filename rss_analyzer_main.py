#!/usr/bin/env python3
"""
RSS Word Frequency Analyzer
A Flask web application that analyzes word frequency from RSS feeds
with customizable feed selection and word filtering.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import feedparser
import re
from collections import Counter
import requests
from urllib.parse import urlparse
import time
from datetime import datetime
import threading
import json
import os

app = Flask(__name__)

class RSSWordAnalyzer:
    def __init__(self):
        self.feeds_data = {}
        self.default_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 
            'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 
            'their', 'am', 'said', 'says', 'say', 'get', 'go', 'going', 'went', 
            'come', 'came', 'time', 'people', 'way', 'day', 'man', 'new', 'first', 
            'last', 'long', 'great', 'little', 'own', 'other', 'old', 'right', 
            'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 
            'important', 'few', 'public', 'bad', 'same', 'able', 'also', 'back', 
            'after', 'use', 'her', 'than', 'now', 'look', 'only', 'think', 'see', 
            'know', 'take', 'work', 'life', 'become', 'here', 'how', 'so', 'get', 
            'want', 'make', 'give', 'hand', 'part', 'place', 'where', 'turn', 
            'put', 'end', 'why', 'try', 'good', 'woman', 'through', 'us', 'down', 
            'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 
            'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very', 
            'what', 'know', 'just', 'first', 'get', 'over', 'think', 'also', 
            'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 
            'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 
            'much', 'too', 'any', 'may', 'well', 'such'
        }
        self.custom_stopwords = set()
        self.selected_feeds = {}
        
        # Default RSS feeds organized by category
        self.default_feeds = {
            # Original defaults
            'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
            'Reuters': 'http://feeds.reuters.com/reuters/topNews',
            'CNN': 'http://rss.cnn.com/rss/edition.rss',
            'TechCrunch': 'http://feeds.feedburner.com/TechCrunch',
            'Hacker News': 'https://hnrss.org/frontpage',
            
            # Technology & Science
            'Ars Technica': 'http://arstechnica.com/feed/',
            'The Register': 'http://www.theregister.co.uk/headlines.atom',
            'Schneier on Security': 'https://www.schneier.com/feed/atom/',
            'Krebs on Security': 'https://krebsonsecurity.com/feed/',
            'NYT Technology': 'http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
            'Slashdot': 'http://rss.slashdot.org/Slashdot/slashdotMain',
            'LA Times Technology': 'http://www.latimes.com/business/technology/rss2.0.xml',
            'GitHub Blog': 'https://github.com/blog/all.atom',
            'Scientific American': 'http://rss.sciam.com/basic-science',
            'Scientific American Global': 'http://rss.sciam.com/ScientificAmerican-Global',
            'Scientific American Technology': 'http://rss.sciam.com/sciam/technology',
            'The RISKS Digest': 'http://catless.ncl.ac.uk/risksatom.xml',
            
            # News & Politics
            'NYT Top Stories': 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
            'NYT US News': 'http://rss.nytimes.com/services/xml/rss/nyt/US.xml',
            'Washington Post Politics': 'http://feeds.washingtonpost.com/rss/politics',
            'NPR Politics': 'http://www.npr.org/rss/rss.php?id=1014',
            'Guardian US': 'http://www.guardian.co.uk/world/usa/rss',
            'ProPublica': 'http://feeds.propublica.org/propublica/main',
            'Talking Points Memo': 'https://talkingpointsmemo.com/news/feed',
            'Naked Capitalism': 'https://www.nakedcapitalism.com/feed',
            'The Real News Network': 'https://therealnews.com/feed?partner-feed=the-real-news-network',
            'Texas Tribune': 'https://feeds.texastribune.org/feeds/main/?_ga=2.223565083.1653973109.1685112376-13535722.1664292644',
            
            # Business & Finance
            'CNBC US Top News': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'WSJ Technology': 'https://feeds.a.dj.com/rss/RSSWSJD.xml',
            'Yahoo Finance': 'https://finance.yahoo.com/news/rss',
            'Nasdaq Data Link Blog': 'https://blog.quandl.com/feed',
            
            # Special Interest
            'Pluralistic (Cory Doctorow)': 'https://pluralistic.net/feed/',
            'Dave Winer': 'http://scripting.com/rss.xml',
            'Web3 is Going Just Great': 'https://web3isgoinggreat.com/feed.xml',
            'Full Disclosure (Security)': 'http://seclists.org/rss/fulldisclosure.rss',
            
            # Reddit Communities
            'r/ESP32': 'https://www.reddit.com/r/esp32.rss',
            'r/HomeAssistant': 'https://www.reddit.com/r/homeassistant.rss',
            'r/PythonPandas': 'https://www.reddit.com/r/PythonPandas.rss',
            'r/AliExpressFinds': 'https://www.reddit.com/r/aliexpressfinds.rss',
            
            # International
            'Pravda Report': 'https://feeds.feedburner.com/engpravda'
        }
        
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file if it exists"""
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.custom_stopwords = set(settings.get('custom_stopwords', []))
                    self.selected_feeds = settings.get('selected_feeds', self.default_feeds.copy())
            except:
                self.selected_feeds = self.default_feeds.copy()
        else:
            self.selected_feeds = self.default_feeds.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'custom_stopwords': list(self.custom_stopwords),
            'selected_feeds': self.selected_feeds
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    def fetch_feed(self, feed_name, feed_url):
        """Fetch and parse a single RSS feed"""
        try:
            # Set timeout and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Parse the feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                print(f"Warning: Issues parsing {feed_name}: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries[:50]:  # Limit to 50 most recent entries
                title = getattr(entry, 'title', '')
                description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
                link = getattr(entry, 'link', '')
                pub_date = getattr(entry, 'published', '')
                
                # Clean HTML tags from description
                description = re.sub('<[^<]+?>', '', description)
                
                articles.append({
                    'title': title,
                    'description': description,
                    'link': link,
                    'published': pub_date,
                    'feed_name': feed_name
                })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching {feed_name}: {str(e)}")
            return []
    
    def extract_words(self, text):
        """Extract words from text, converting to lowercase and removing punctuation"""
        if not text:
            return []
        
        # Convert to lowercase and extract words (letters only, minimum 3 characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return words
    
    def analyze_feeds(self):
        """Fetch all selected feeds and analyze word frequency"""
        all_articles = []
        
        # Fetch all feeds
        for feed_name, feed_url in self.selected_feeds.items():
            print(f"Fetching {feed_name}...")
            articles = self.fetch_feed(feed_name, feed_url)
            all_articles.extend(articles)
        
        if not all_articles:
            return pd.DataFrame(), pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(all_articles)
        
        # Extract all words
        all_words = []
        for _, article in df.iterrows():
            title_words = self.extract_words(article['title'])
            desc_words = self.extract_words(article['description'])
            all_words.extend(title_words + desc_words)
        
        # Filter out stopwords
        all_stopwords = self.default_stopwords.union(self.custom_stopwords)
        filtered_words = [word for word in all_words if word not in all_stopwords]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Create word frequency DataFrame
        word_freq_df = pd.DataFrame([
            {'word': word, 'frequency': count}
            for word, count in word_counts.most_common(200)
        ])
        
        return df, word_freq_df

# Initialize the analyzer
analyzer = RSSWordAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/feeds')
def get_feeds():
    """Get current feed selection"""
    return jsonify({
        'selected_feeds': analyzer.selected_feeds,
        'default_feeds': analyzer.default_feeds
    })

@app.route('/api/feeds', methods=['POST'])
def update_feeds():
    """Update feed selection"""
    data = request.json
    if 'feeds' in data:
        analyzer.selected_feeds = data['feeds']
        analyzer.save_settings()
    return jsonify({'status': 'success'})

@app.route('/api/stopwords')
def get_stopwords():
    """Get current stopwords"""
    return jsonify({
        'custom_stopwords': list(analyzer.custom_stopwords),
        'default_count': len(analyzer.default_stopwords)
    })

@app.route('/api/stopwords', methods=['POST'])
def update_stopwords():
    """Update custom stopwords"""
    data = request.json
    if 'stopwords' in data:
        analyzer.custom_stopwords = set(data['stopwords'])
        analyzer.save_settings()
    return jsonify({'status': 'success'})

@app.route('/api/analyze')
def analyze():
    """Perform analysis and return results"""
    try:
        articles_df, word_freq_df = analyzer.analyze_feeds()
        
        return jsonify({
            'articles': articles_df.to_dict('records') if not articles_df.empty else [],
            'word_frequency': word_freq_df.to_dict('records') if not word_freq_df.empty else [],
            'total_articles': len(articles_df),
            'total_unique_words': len(word_freq_df),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting RSS Word Frequency Analyzer...")
    print("📊 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)