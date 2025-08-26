# 📊 RSS Word Frequency Analyzer

A modern web application that analyzes word frequency from RSS feeds with customizable feed selection and intelligent word filtering. Built with Flask and featuring a responsive, interactive interface.

![RSS Word Frequency Analyzer](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-3.0.0-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 📡 **RSS Feed Management**
- **40+ Pre-configured feeds** from major news sources, tech blogs, and communities
- **Categorized feeds** (News & Politics, Technology & Science, Business & Finance, etc.)
- **Custom RSS feed support** - Add any RSS/Atom feed
- **Collapsible categories** with bulk select/deselect options
- **Automatic feed validation** and error handling

### 🧠 **Smart Word Analysis**
- **Advanced text processing** using pandas for efficiency
- **Intelligent stopword filtering** with 100+ common words excluded by default
- **Custom stopwords** - Add domain-specific terms to exclude
- **Minimum word length filtering** (3+ characters)
- **HTML tag removal** and text cleaning
- **Case-insensitive processing**

### 📊 **Interactive Results Display**
- **Dynamic word cloud** with frequency-based sizing
- **Comprehensive word frequency table** with rankings and percentages
- **Flexible display limits** - Show top 10, 25, 50, 100, 200, 500, or all words
- **Real-time limit adjustment** without re-running analysis
- **Article source breakdown** showing contribution from each feed
- **Responsive design** that works on all screen sizes

### 🔧 **Technical Features**
- **Persistent settings** - Your feed selections and stopwords are saved
- **Comprehensive debugging** with detailed console logging
- **Error handling** with user-friendly messages
- **Modern UI** with gradient backgrounds and smooth animations
- **Performance optimized** for handling large datasets

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/rss-word-analyzer.git
   cd rss-word-analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python rss_analyzer.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

## 📖 Usage Guide

### Getting Started
1. **Select RSS Feeds** - Choose from organized categories or add custom feeds
2. **Configure Stopwords** (Optional) - Add words you want to exclude from analysis
3. **Set Display Limit** - Choose how many top words to display
4. **Run Analysis** - Click "Analyze Word Frequency" to process the feeds
5. **Explore Results** - View word clouds, frequency tables, and source articles

### Feed Categories

**📺 News & Politics**
- NYT (Top Stories, US News, Technology), Guardian US, Washington Post, NPR, ProPublica, and more

**💻 Technology & Science**
- Ars Technica, The Register, Schneier/Krebs Security, GitHub Blog, Scientific American, Slashdot

**💼 Business & Finance**
- CNBC, Wall Street Journal, Yahoo Finance, Nasdaq Data Link

**🎯 Special Interest**
- Pluralistic (Cory Doctorow), Web3 is Going Just Great, Security disclosures

**💬 Reddit Communities**
- r/ESP32, r/HomeAssistant, r/PythonPandas, r/AliExpressFinds

**🌍 International**
- International news sources and perspectives

### Advanced Features

#### Custom Stopwords
Add domain-specific terms to exclude from analysis:
```
bitcoin
cryptocurrency
covid
pandemic
```

#### Display Limits
- **Top 10** - Essential themes only (great for presentations)
- **Top 25** - Key concepts overview
- **Top 50** - Balanced analysis (default)
- **Top 100** - Detailed insights
- **Top 200+** - Comprehensive analysis
- **All Words** - Complete linguistic breakdown

## 🏗️ Architecture

### Backend (Python/Flask)
- **Flask web framework** for REST API endpoints
- **pandas** for efficient data processing and analysis
- **feedparser** for robust RSS/Atom feed parsing
- **requests** for HTTP communication with feed sources
- **Counter** from collections for word frequency analysis

### Frontend (HTML/CSS/JavaScript)
- **Vanilla JavaScript** for dynamic interactions
- **CSS Grid and Flexbox** for responsive layouts
- **Gradient designs** with modern visual effects
- **Asynchronous communication** with fetch API
- **Real-time debugging** with comprehensive console logging

### Data Flow
1. User selects RSS feeds and configuration
2. Flask backend fetches and parses RSS feeds
3. Text extraction and cleaning with regex
4. Word frequency analysis using pandas and Counter
5. JSON response with structured data
6. Frontend renders interactive visualizations

## 📁 Project Structure

```
rss-word-analyzer/
│
├── rss_analyzer.py          # Main Flask application
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
│
├── templates/
│   └── index.html          # HTML template (auto-generated)
│
├── settings.json           # User settings (auto-created)
│
└── .gitignore             # Git ignore file (recommended)
```

## 🛠️ Development

### Adding New Feed Sources
Feeds are categorized automatically based on keywords in the `categorizeFeeds()` function. To add new default feeds, edit the `default_feeds` dictionary in `rss_analyzer.py`.

### Customizing Stopwords
Default stopwords are defined in the `default_stopwords` set. Users can add custom stopwords through the web interface, which are saved in `settings.json`.

### Debugging
The application includes comprehensive logging. Open browser DevTools (F12) → Console to see detailed execution flow and error messages.

## 🚨 Troubleshooting

### Common Issues

**No results displayed:**
- Check browser console for JavaScript errors
- Verify at least one RSS feed is selected
- Ensure feeds are accessible (not behind paywalls/auth)

**Feed fetching fails:**
- Some feeds may be temporarily unavailable
- Corporate firewalls might block certain RSS sources
- Try different feeds or add custom feeds

**Performance issues:**
- Reduce the number of selected feeds
- Use smaller display limits (Top 10-50)
- Some feeds with large articles may be slow to process

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **RSS Feed Sources** - Thanks to all the news organizations and bloggers providing RSS feeds
- **OPML Source** - Feed list inspired by tt-rss community configurations
- **Libraries** - Built with Flask, pandas, feedparser, and other excellent Python libraries

## 📊 Stats

- **40+ RSS feeds** pre-configured
- **6 organized categories** for easy selection
- **100+ default stopwords** for clean analysis
- **Responsive design** works on desktop, tablet, and mobile
- **Real-time processing** of thousands of articles
- **Comprehensive error handling** with user-friendly messages

---

**Made with ❤️ for the data analysis and RSS community**

*If you find this useful, please star the repository and share with others!* ⭐
