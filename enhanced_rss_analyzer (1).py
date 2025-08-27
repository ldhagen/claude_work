#!/usr/bin/env python3
"""
RSS Word Frequency Analyzer
A Flask web application that analyzes word frequency from RSS feeds
with customizable feed selection and word filtering, now with source links.
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
        """Fetch all selected feeds and analyze word frequency with source tracking"""
        all_articles = []
        feed_word_counts = {}
        feed_word_sources = {}  # Track which articles contain each word
        
        # Fetch all feeds
        for feed_name, feed_url in self.selected_feeds.items():
            print(f"Fetching {feed_name}...")
            articles = self.fetch_feed(feed_name, feed_url)
            all_articles.extend(articles)
            
            # Track word counts and sources by feed
            feed_words = []
            word_to_articles = {}  # Map words to articles that contain them
            
            for article in articles:
                title_words = self.extract_words(article['title'])
                desc_words = self.extract_words(article['description'])
                article_words = set(title_words + desc_words)  # Use set to avoid double-counting words in same article
                
                feed_words.extend(title_words + desc_words)
                
                # Track which articles contain which words
                for word in article_words:
                    if word not in word_to_articles:
                        word_to_articles[word] = []
                    word_to_articles[word].append({
                        'title': article['title'],
                        'link': article['link'],
                        'published': article['published']
                    })
            
            # Filter out stopwords for this feed
            all_stopwords = self.default_stopwords.union(self.custom_stopwords)
            filtered_feed_words = [word for word in feed_words if word not in all_stopwords]
            feed_word_counts[feed_name] = Counter(filtered_feed_words)
            
            # Store source information for filtered words
            feed_word_sources[feed_name] = {}
            for word in feed_word_counts[feed_name]:
                if word in word_to_articles:
                    feed_word_sources[feed_name][word] = word_to_articles[word]
        
        if not all_articles:
            return pd.DataFrame(), pd.DataFrame(), {}, {}
        
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
        
        return df, word_freq_df, feed_word_counts, feed_word_sources

def create_html_template():
    """Create the HTML template content with enhanced source link display"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSS Word Frequency Analyzer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .content { padding: 30px; }
        .section {
            margin-bottom: 30px;
            padding: 25px;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .section h2 { color: #2c3e50; margin-bottom: 20px; font-size: 1.4rem; }
        .feed-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .feed-controls .btn {
            font-size: 0.9rem;
            padding: 8px 16px;
        }
        .feed-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #dee2e6;
            margin-bottom: 10px;
        }
        .feed-item label { display: flex; align-items: center; cursor: pointer; }
        .feed-item input { margin-right: 10px; }
        .custom-feed { display: flex; gap: 10px; margin-top: 15px; }
        .custom-feed input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn-secondary {
            background: none;
            border: 1px solid #667eea;
            color: #667eea;
        }
        .btn-secondary:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        .stopwords-input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            min-height: 100px;
            font-family: inherit;
        }
        .results-section { display: none; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
        .word-cloud { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 30px; }
        .word-tag {
            background: #e9ecef;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            border: 1px solid #dee2e6;
        }
        .word-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .word-table th, .word-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .word-table th { background: #f8f9fa; font-weight: 600; }
        .loading { text-align: center; padding: 40px; color: #6c757d; }
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .success {
            color: #155724;
            background: #d4edda;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .feed-breakdown {
            margin-top: 30px;
        }
        .feed-breakdown h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }
        .feed-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        .feed-tab {
            padding: 10px 16px;
            border: none;
            background: none;
            color: #6c757d;
            cursor: pointer;
            border-radius: 6px 6px 0 0;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .feed-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .feed-tab:hover:not(.active) {
            background: #f8f9fa;
            color: #495057;
        }
        .feed-content {
            display: none;
        }
        .feed-content.active {
            display: block;
        }
        .feed-word-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 20px;
        }
        .feed-word-tag {
            background: #e3f2fd;
            border: 1px solid #90caf9;
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 0.85rem;
            color: #1565c0;
            cursor: pointer;
            transition: all 0.2s;
        }
        .feed-word-tag:hover {
            background: #90caf9;
            color: white;
        }
        .word-sources {
            margin-top: 20px;
            background: white;
            border-radius: 6px;
            padding: 20px;
            border: 1px solid #e1e5e9;
        }
        .word-sources h4 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        .source-links {
            display: grid;
            gap: 12px;
        }
        .source-link {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
            transition: all 0.2s;
        }
        .source-link:hover {
            background: #e9ecef;
            transform: translateY(-1px);
        }
        .source-link a {
            text-decoration: none;
            color: #495057;
            font-weight: 500;
            display: block;
            margin-bottom: 4px;
        }
        .source-link a:hover {
            color: #667eea;
        }
        .source-date {
            font-size: 0.85rem;
            color: #6c757d;
        }
        .enhanced-word-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .enhanced-word-table th,
        .enhanced-word-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .enhanced-word-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        .word-row {
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .word-row:hover {
            background-color: #f8f9fa;
        }
        .word-row.expanded {
            background-color: #e3f2fd;
        }
        .sources-row {
            display: none;
        }
        .sources-row.show {
            display: table-row;
        }
        .sources-cell {
            background: #f0f8ff;
            border: 1px solid #90caf9;
            padding: 15px;
        }
        .sources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 10px;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 8px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        .modal-header h3 {
            color: #2c3e50;
            font-size: 1.3rem;
        }
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }
        .close:hover {
            color: #667eea;
        }
    </style>
</head>"""

    html_content += """
<body>
    <div class="container">
        <div class="header">
            <h1>RSS Word Frequency Analyzer</h1>
            <p>Analyze word frequency from your favorite RSS feeds with source tracking</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>RSS Feed Selection</h2>
                <div class="feed-controls">
                    <button class="btn btn-secondary" onclick="selectAllFeeds()">Select All</button>
                    <button class="btn btn-secondary" onclick="deselectAllFeeds()">Deselect All</button>
                </div>
                <div id="feeds-container"></div>
                <div class="custom-feed">
                    <input type="text" id="custom-feed-name" placeholder="Feed Name">
                    <input type="url" id="custom-feed-url" placeholder="RSS Feed URL">
                    <button class="btn" onclick="addCustomFeed()">Add Feed</button>
                </div>
            </div>
            
            <div class="section">
                <h2>Custom Stop Words</h2>
                <textarea id="stopwords" class="stopwords-input" 
                         placeholder="Enter words to exclude, one per line..."></textarea>
                <button class="btn" onclick="saveStopwords()" style="margin-top: 15px;">Save Stop Words</button>
            </div>
            
            <div class="section">
                <h2>Analysis</h2>
                <button class="btn" id="analyze-btn" onclick="performAnalysis()">Analyze Word Frequency</button>
                <div id="loading" class="loading" style="display: none;">
                    <p>Fetching and analyzing RSS feeds...</p>
                </div>
            </div>
            
            <div class="section results-section" id="results-section">
                <h2>Results</h2>
                <div id="stats" class="stats"></div>
                <div id="word-cloud" class="word-cloud"></div>
                <table class="word-table">
                    <thead>
                        <tr><th>Rank</th><th>Word</th><th>Frequency</th></tr>
                    </thead>
                    <tbody id="word-table-body"></tbody>
                </table>
                
                <div class="feed-breakdown" id="feed-breakdown">
                    <h3>Word Frequency by Feed with Source Articles</h3>
                    <div class="feed-tabs" id="feed-tabs"></div>
                    <div id="feed-contents"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for word sources -->
    <div id="word-sources-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modal-word-title">Articles containing word</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div id="modal-sources-content"></div>
        </div>
    </div>

    <script>
        let currentFeeds = {};
        let currentResults = null;
        let currentWordSources = null;
        
        document.addEventListener('DOMContentLoaded', function() {
            loadFeeds();
            loadStopwords();
        });
        
        async function loadFeeds() {
            try {
                const response = await fetch('/api/feeds');
                const data = await response.json();
                currentFeeds = data.selected_feeds;
                renderFeeds(data.selected_feeds, data.default_feeds);
            } catch (error) {
                showError('Error loading feeds: ' + error.message);
            }
        }
        
        function renderFeeds(selectedFeeds, defaultFeeds) {
            const container = document.getElementById('feeds-container');
            container.innerHTML = '';
            
            for (const [name, url] of Object.entries(defaultFeeds)) {
                const feedItem = document.createElement('div');
                feedItem.className = 'feed-item';
                feedItem.innerHTML = '<label><input type="checkbox" ' + 
                    (selectedFeeds[name] ? 'checked' : '') + 
                    ' onchange="toggleFeed(\\'' + name.replace(/'/g, "\\'") + '\\', \\'' + url.replace(/'/g, "\\'") + '\\', this.checked)"><div><strong>' + 
                    name + '</strong><br><small style="color: #6c757d;">' + 
                    (url.length > 50 ? url.substring(0, 50) + '...' : url) + '</small></div></label>';
                container.appendChild(feedItem);
            }
        }
        
        function selectAllFeeds() {
            const checkboxes = document.querySelectorAll('#feeds-container input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                if (!checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
        }
        
        function deselectAllFeeds() {
            const checkboxes = document.querySelectorAll('#feeds-container input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    checkbox.checked = false;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
        }
        
        function toggleFeed(name, url, checked) {
            if (checked) {
                currentFeeds[name] = url;
            } else {
                delete currentFeeds[name];
            }
            saveFeeds();
        }
        
        async function saveFeeds() {
            try {
                await fetch('/api/feeds', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({feeds: currentFeeds})
                });
            } catch (error) {
                showError('Error saving feeds: ' + error.message);
            }
        }
        
        function addCustomFeed() {
            const name = document.getElementById('custom-feed-name').value.trim();
            const url = document.getElementById('custom-feed-url').value.trim();
            
            if (!name || !url) {
                showError('Please enter both feed name and URL');
                return;
            }
            
            currentFeeds[name] = url;
            saveFeeds();
            loadFeeds();
            
            document.getElementById('custom-feed-name').value = '';
            document.getElementById('custom-feed-url').value = '';
            
            showSuccess('Custom feed added successfully!');
        }
        
        async function loadStopwords() {
            try {
                const response = await fetch('/api/stopwords');
                const data = await response.json();
                document.getElementById('stopwords').value = data.custom_stopwords.join('\\n');
            } catch (error) {
                showError('Error loading stopwords: ' + error.message);
            }
        }
        
        async function saveStopwords() {
            const stopwordsText = document.getElementById('stopwords').value;
            const stopwords = stopwordsText.split('\\n')
                .map(word => word.trim().toLowerCase())
                .filter(word => word.length > 0);
            
            try {
                await fetch('/api/stopwords', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({stopwords: stopwords})
                });
                showSuccess('Stop words saved successfully!');
            } catch (error) {
                showError('Error saving stopwords: ' + error.message);
            }
        }
        
        async function performAnalysis() {
            if (Object.keys(currentFeeds).length === 0) {
                showError('Please select at least one RSS feed');
                return;
            }
            
            const analyzeBtn = document.getElementById('analyze-btn');
            const loading = document.getElementById('loading');
            const resultsSection = document.getElementById('results-section');
            
            analyzeBtn.disabled = true;
            loading.style.display = 'block';
            resultsSection.style.display = 'none';
            
            try {
                const response = await fetch('/api/analyze');
                const data = await response.json();
                
                if (data.error) {
                    showError('Analysis error: ' + data.error);
                    return;
                }
                
                displayResults(data);
                resultsSection.style.display = 'block';
                
            } catch (error) {
                showError('Error performing analysis: ' + error.message);
            } finally {
                analyzeBtn.disabled = false;
                loading.style.display = 'none';
            }
        }
        
        function displayResults(data) {
            currentResults = data;
            currentWordSources = data.feed_word_sources || {};
            
            document.getElementById('stats').innerHTML = 
                '<div class="stat-card"><div class="stat-number">' + (data.total_articles || 0) + 
                '</div><div>Articles Analyzed</div></div>' +
                '<div class="stat-card"><div class="stat-number">' + (data.total_unique_words || 0) + 
                '</div><div>Unique Words</div></div>' +
                '<div class="stat-card"><div class="stat-number">' + Object.keys(currentFeeds).length + 
                '</div><div>RSS Feeds</div></div>';
            
            if (data.word_frequency && data.word_frequency.length > 0) {
                displayWordCloud(data.word_frequency.slice(0, 50));
                displayWordTable(data.word_frequency);
            }
            
            if (data.feed_word_counts) {
                displayFeedBreakdown(data.feed_word_counts);
            }
        }
        
        function displayWordCloud(wordFrequency) {
            const wordCloud = document.getElementById('word-cloud');
            wordCloud.innerHTML = '';
            
            wordFrequency.forEach((item, index) => {
                const wordTag = document.createElement('span');
                wordTag.className = 'word-tag';
                const fontSize = Math.max(0.8, 1.2 - (index / 50) * 0.4);
                wordTag.style.fontSize = fontSize + 'rem';
                wordTag.textContent = item.word + ' (' + item.frequency + ')';
                wordCloud.appendChild(wordTag);
            });
        }
        
        function displayWordTable(wordFrequency) {
            const tableBody = document.getElementById('word-table-body');
            tableBody.innerHTML = '';
            
            wordFrequency.slice(0, 100).forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = '<td>' + (index + 1) + '</td><td><strong>' + 
                    item.word + '</strong></td><td>' + item.frequency + '</td>';
                tableBody.appendChild(row);
            });
        }
        
        function displayFeedBreakdown(feedWordCounts) {
            const feedTabs = document.getElementById('feed-tabs');
            const feedContents = document.getElementById('feed-contents');
            
            feedTabs.innerHTML = '';
            feedContents.innerHTML = '';
            
            const feedNames = Object.keys(feedWordCounts);
            
            feedNames.forEach((feedName, index) => {
                // Create tab
                const tab = document.createElement('button');
                tab.className = 'feed-tab' + (index === 0 ? ' active' : '');
                tab.textContent = feedName;
                tab.onclick = () => showFeedContent(feedName);
                feedTabs.appendChild(tab);
                
                // Create content
                const content = document.createElement('div');
                content.className = 'feed-content' + (index === 0 ? ' active' : '');
                content.id = 'feed-content-' + index;
                
                const words = feedWordCounts[feedName];
                if (words && words.length > 0) {
                    // Word cloud for this feed with clickable tags
                    const feedWordCloud = document.createElement('div');
                    feedWordCloud.className = 'feed-word-cloud';
                    
                    words.slice(0, 20).forEach(item => {
                        const wordTag = document.createElement('span');
                        wordTag.className = 'feed-word-tag';
                        wordTag.textContent = item.word + ' (' + item.frequency + ')';
                        wordTag.onclick = () => showWordSources(item.word, feedName);
                        wordTag.title = 'Click to see source articles';
                        feedWordCloud.appendChild(wordTag);
                    });
                    
                    content.appendChild(feedWordCloud);
                    
                    // Enhanced table for this feed with expandable rows
                    const table = document.createElement('table');
                    table.className = 'enhanced-word-table';
                    table.innerHTML = '<thead><tr><th>Rank</th><th>Word</th><th>Frequency</th><th>Sources</th></tr></thead>';
                    
                    const tbody = document.createElement('tbody');
                    words.slice(0, 25).forEach((item, i) => {
                        // Main word row
                        const row = document.createElement('tr');
                        row.className = 'word-row';
                        row.dataset.word = item.word;
                        row.dataset.feedName = feedName;
                        row.innerHTML = '<td>' + (i + 1) + '</td><td><strong>' + 
                            item.word + '</strong></td><td>' + item.frequency + '</td><td>' +
                            '<button class="btn btn-secondary" style="font-size: 0.8rem; padding: 4px 8px;" onclick="showWordSources(\\'' + 
                            item.word.replace(/'/g, "\\'") + '\\', \\'' + feedName.replace(/'/g, "\\'") + '\\')">View Sources</button></td>';
                        tbody.appendChild(row);
                    });
                    table.appendChild(tbody);
                    content.appendChild(table);
                } else {
                    content.innerHTML = '<p style="color: #6c757d; padding: 20px;">No words found for this feed.</p>';
                }
                
                feedContents.appendChild(content);
            });
        }
        
        function showFeedContent(feedName) {
            // Update tabs
            const tabs = document.querySelectorAll('.feed-tab');
            const contents = document.querySelectorAll('.feed-content');
            
            tabs.forEach(tab => {
                if (tab.textContent === feedName) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
            
            // Update content
            contents.forEach((content, index) => {
                const tabText = document.querySelectorAll('.feed-tab')[index].textContent;
                if (tabText === feedName) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        }
        
        function showWordSources(word, feedName) {
            const modal = document.getElementById('word-sources-modal');
            const modalTitle = document.getElementById('modal-word-title');
            const modalContent = document.getElementById('modal-sources-content');
            
            modalTitle.textContent = 'Articles containing "' + word + '" from ' + feedName;
            
            // Get sources for this word from this feed
            const sources = currentWordSources[feedName] && currentWordSources[feedName][word] || [];
            
            if (sources.length === 0) {
                modalContent.innerHTML = '<p style="color: #6c757d;">No source articles found for this word.</p>';
            } else {
                let sourcesHtml = '<div class="sources-grid">';
                sources.forEach(source => {
                    const publishedDate = source.published ? new Date(source.published).toLocaleDateString() : 'Unknown date';
                    sourcesHtml += '<div class="source-link">';
                    if (source.link) {
                        sourcesHtml += '<a href="' + source.link + '" target="_blank" rel="noopener noreferrer">' + 
                            (source.title || 'Untitled Article') + '</a>';
                    } else {
                        sourcesHtml += '<span>' + (source.title || 'Untitled Article') + '</span>';
                    }
                    sourcesHtml += '<div class="source-date">' + publishedDate + '</div>';
                    sourcesHtml += '</div>';
                });
                sourcesHtml += '</div>';
                modalContent.innerHTML = sourcesHtml;
            }
            
            modal.style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('word-sources-modal').style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('word-sources-modal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
        
        function showError(message) {
            const existing = document.querySelector('.error');
            if (existing) existing.remove();
            
            const error = document.createElement('div');
            error.className = 'error';
            error.textContent = message;
            document.querySelector('.content').insertBefore(error, document.querySelector('.content').firstChild);
            
            setTimeout(() => error.remove(), 8000);
        }
        
        function showSuccess(message) {
            const existing = document.querySelector('.success');
            if (existing) existing.remove();
            
            const success = document.createElement('div');
            success.className = 'success';
            success.textContent = message;
            document.querySelector('.content').insertBefore(success, document.querySelector('.content').firstChild);
            
            setTimeout(() => success.remove(), 3000);
        }
    </script>
</body>
</html>"""
    
    return html_content

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
    """Perform analysis and return results with source tracking"""
    try:
        articles_df, word_freq_df, feed_word_counts, feed_word_sources = analyzer.analyze_feeds()
        
        # Format feed word counts for JSON
        formatted_feed_counts = {}
        for feed_name, word_counter in feed_word_counts.items():
            formatted_feed_counts[feed_name] = [
                {'word': word, 'frequency': count}
                for word, count in word_counter.most_common(50)
            ]
        
        # Format feed word sources for JSON
        formatted_feed_sources = {}
        for feed_name, word_sources in feed_word_sources.items():
            formatted_feed_sources[feed_name] = {}
            for word, sources in word_sources.items():
                # Limit to top 10 sources per word to avoid overwhelming the interface
                formatted_feed_sources[feed_name][word] = sources[:10]
        
        return jsonify({
            'articles': articles_df.to_dict('records') if not articles_df.empty else [],
            'word_frequency': word_freq_df.to_dict('records') if not word_freq_df.empty else [],
            'feed_word_counts': formatted_feed_counts,
            'feed_word_sources': formatted_feed_sources,
            'total_articles': len(articles_df),
            'total_unique_words': len(word_freq_df),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory and HTML template if they don't exist
    os.makedirs('templates', exist_ok=True)
    
    # Write the HTML template
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(create_html_template())
    
    print("Starting Enhanced RSS Word Frequency Analyzer...")
    print("New features:")
    print("- Click on word tags to see source articles")
    print("- 'View Sources' buttons in word frequency tables")
    print("- Modal popups showing article titles, links, and dates")
    print("- Enhanced source tracking and attribution")
    print("")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)