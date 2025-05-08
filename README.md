# Best Buddies Website Scraper

This Python project scrapes all static and dynamic content (including FAQs) from the Best Buddies Qatar website.

## Features
- Extracts internal links within the domain
- Uses Selenium to handle dynamic FAQ pagination
- Saves pages as structured JSON files
- Records visited and unvisited URLs in CSV format

## Requirements
- Python 3.7+
- Google Chrome and ChromeDriver
- `pip install -r requirements.txt`

## Usage
```bash
python scraper/main.py
```

## Output
- Scraped JSON files are saved in `website_content/`
- URL logs saved in CSV files
