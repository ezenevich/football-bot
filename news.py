from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from config import HEADERS

NewsItem = Dict[str, str]


def _parse_championat(limit: int = 5) -> List[NewsItem]:
    url = "https://www.championat.com/football/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    result: List[NewsItem] = []
    for item in soup.select('.news-item__content')[:limit]:
        title = item.select_one('.news-item__title')
        link_tag = item.find('a')
        if not title or not link_tag or not link_tag.get('href'):
            continue
        link = link_tag['href']
        result.append({
            'title': title.get_text(strip=True),
            'link': f"https://www.championat.com{link}" if link.startswith('/') else link,
        })
    return result


def _parse_sportsru(limit: int = 5) -> List[NewsItem]:
    url = "https://www.sports.ru/football/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    result: List[NewsItem] = []
    for item in soup.select('.material-list__item-text')[:limit]:
        title_tag = item.select_one('.material-list__title-link')
        if not title_tag:
            continue
        result.append({
            'title': title_tag.get_text(strip=True),
            'link': title_tag['href'],
        })
    return result


def _parse_eurofootball(limit: int = 5) -> List[NewsItem]:
    url = "https://www.euro-football.ru/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    result: List[NewsItem] = []
    for item in soup.select('.main-news-items-widget__item-title')[:limit]:
        title_tag = item.select_one('a')
        if not title_tag:
            continue
        link = title_tag['href']
        result.append({
            'title': title_tag.get_text(strip=True),
            'link': f"https://www.championat.com{link}" if link.startswith('/') else link,
        })
    return result


def fetch_all_news(limit: int = 5) -> Dict[str, List[NewsItem]]:
    return {
        'Championat.com': _parse_championat(limit),
        'Sports.ru': _parse_sportsru(limit),
        'Euro-Football.ru': _parse_eurofootball(limit),
    }
