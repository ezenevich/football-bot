from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from typing import List, Dict

from config import HEADERS


TransferItem = Dict[str, str]


def _parse_transfermarkt(limit: int = 5) -> List[TransferItem]:
    url = "https://www.transfermarkt.com/neueste-transfergeruechte/geruechte"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for row in soup.select('.odd, .even')[:limit]:
        player = row.select_one('.spielprofil_tooltip')
        clubs = row.select('.vereinprofil_tooltip')
        value = row.select_one('.rechts.hauptlink')
        if player and len(clubs) >= 2:
            transfers.append({
                'player': player.text.strip(),
                'from': clubs[0].text.strip(),
                'to': clubs[1].text.strip(),
                'value': value.text.strip() if value else '?',
                'link': f"https://www.transfermarkt.com{player['href']}",
            })
    return transfers


def _parse_sportsru(limit: int = 5) -> List[TransferItem]:
    url = "https://www.sports.ru/tags/24459/transfers/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for item in soup.select('.short-text')[:limit]:
        title_tag = item.select_one('a')
        if not title_tag:
            continue
        transfers.append({
            'player': title_tag.get_text(strip=True),
            'from': '-',
            'to': '-',
            'value': '-',
            'link': title_tag['href'],
        })
    return transfers


def _parse_eurofootball(limit: int = 5) -> List[TransferItem]:
    url = "https://www.euro-football.ru/transfers"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for row in soup.select('.item-transfer')[:limit]:
        player_tag = row.select_one('.player')
        clubs = row.select('.team')
        if player_tag and len(clubs) >= 2:
            transfers.append({
                'player': player_tag.get_text(strip=True),
                'from': clubs[0].get_text(strip=True),
                'to': clubs[1].get_text(strip=True),
                'value': '-',
                'link': row.find('a')['href'] if row.find('a') else '#',
            })
    return transfers


def _parse_skysports(limit: int = 5) -> List[TransferItem]:
    """Parse transfer rumours from Sky Sports."""
    url = "https://www.skysports.com/transfer-news"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for item in soup.select('.news-list__item')[:limit]:
        headline = item.select_one('.news-list__headline')
        link_tag = item.select_one('a')
        if not headline or not link_tag:
            continue
        transfers.append({
            'player': headline.get_text(strip=True),
            'from': '-',
            'to': '-',
            'value': '-',
            'link': link_tag['href'],
        })
    return transfers


def fetch_all_transfers(limit: int = 5) -> Dict[str, List[TransferItem]]:
    return {
        'Transfermarkt': _parse_transfermarkt(limit),
        'Sports.ru': _parse_sportsru(limit),
        'Euro-Football': _parse_eurofootball(limit),
        'SkySports': _parse_skysports(limit),
    }
