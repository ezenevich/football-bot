from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from typing import List, Dict

from config import HEADERS

TransferItem = Dict[str, str]


def _parse_transfermarkt(limit: int = 5) -> List[TransferItem]:
    url = "https://www.transfermarkt.com/transfers/neuestetransfers/statistik?land_id=0&wettbewerb_id=alle&minMarktwert=500000&maxMarktwert=500000000"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for row in soup.select('.odd, .even')[:limit]:
        row_tags = row.select('.hauptlink')
        player = row_tags[0].text.strip() if row_tags[0] else ''
        club_from = row_tags[1].text.strip() if row_tags[1] else ''
        club_to = row_tags[2].text.strip() if row_tags[2] else ''
        value = row_tags[3].text.strip() if row_tags[3] else '?'
        link = row_tags[0].find('a')['href']

        if club_to == "Without Club":
            continue

        if len(transfers) == 5:
            continue

        transfers.append({
            'player': player,
            'from': club_from,
            'to': club_to,
            'value': value,
            'link': f"https://www.transfermarkt.com{link}",
        })
    return transfers


def _parse_sportsru(limit: int = 5) -> List[TransferItem]:
    url = "https://www.sports.ru/football/transfers/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for item in soup.select('.transfers-table__row')[:limit]:
        title_tag = item.select_one('.transfers-table__body-span.transfers-table__name').find('a')
        clubs_tag = item.select('.transfers-table__club-item')
        if len(clubs_tag) >= 2:
            old = clubs_tag[0].get_text(strip=True)
            new = clubs_tag[1].get_text(strip=True)
        else:
            old = ""
            new = ""

        value = item.select_one('.transfers-table__body-span.transfers-table__sum')

        transfers.append({
            'player': title_tag.text.strip(),
            'from': old,
            'to': new,
            'value': value.text.strip() if value and value.text.strip() != '-' else '?',
            'link': title_tag['href'],
        })
    return transfers


def _parse_eurofootball(limit: int = 5) -> List[TransferItem]:
    url = "https://www.euro-football.ru/transfer"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for row in soup.select('.transfer-person-widget__item')[:limit]:
        player_tag = row.select_one('.transfer-person-widget__name')
        teams_tag = row.select_one('.transfer-person-widget__teams').findAll('a')
        value = row.select_one('.transfer-person-widget__state-type')
        if len(teams_tag) >= 2:
            old = teams_tag[0].get_text(strip=True)
            new = teams_tag[1].get_text(strip=True)
        else:
            old = ""
            new = ""
        link = f"https://www.euro-football.ru{player_tag['href']}" if player_tag and player_tag.has_attr(
            'href') else '#'

        transfers.append({
            'player': player_tag.text.strip(),
            'from': old,
            'to': new,
            'value': value.text.strip() if value else '?',
            'link': link,
        })
    return transfers


def _parse_tribuna(limit: int = 5) -> List[TransferItem]:
    url = "https://ua.tribuna.com/football/other/transfers/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    transfers: List[TransferItem] = []
    for row in soup.select('.Transfers-module_transfer__item_UROTu__Main')[:limit]:
        print(row)
        link = row.find('a')['href']
        player = row.select_one('.NewUiText-module_text--subtitle-1_EbJBq__Main').text.strip()
        value = row.select_one('.Transfers-module_transfer__item--span_rh8MN__Main').text.strip()
        old = row.select_one('[data-test="tag-transfers-widget-team-from"]').find('a')['href']
        new = row.select_one('[data-test="tag-transfers-widget-team-to"]').find('a')['href']

        transfers.append({
            'player': player,
            'from': old,
            'to': new,
            'value': value,
            'link': link,
        })
        return transfers


def fetch_all_transfers(limit: int = 5) -> Dict[str, List[TransferItem]]:
    return {
        'Transfermarkt.com': _parse_transfermarkt(25),
        'Sports.ru': _parse_sportsru(limit),
        'Euro-Football.ru': _parse_eurofootball(limit),
    }
