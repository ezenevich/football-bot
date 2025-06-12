from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

from config import HEADERS

MatchItem = Dict[str, str]


def _parse_championat(limit: int = 5) -> List[MatchItem]:
    url = f"https://www.championat.com/football"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    for item in soup.select('.livetable-event')[:limit]:
        date_tag = item.select_one('.livetable-event__time')
        name_tags = item.select('.team-name')
        result_tag = item.select_one('.livetable-event__result')
        status_tag = item.select_one('.livetable-event__status')
        if not name_tags:
            continue
        if len(name_tags) >= 2:
            teams = f"{name_tags[0].get_text(strip=True)} - {name_tags[1].get_text(strip=True)}"
        else:
            teams = name_tags[0].get_text(strip=True)
        link_tag = item.find('a')
        link = link_tag['href']
        matches.append({
            'time': date_tag.get_text(strip=True) if date_tag else '?',
            'teams': teams,
            'score': result_tag.get_text(strip=True) if result_tag else 'vs',
            'tournament': status_tag.get_text(strip=True) if status_tag else '',
            'link': f"https://www.championat.com{link}" if link.startswith('/') else link,
        })
    return matches


def _parse_sportsru(limit: int = 5) -> List[MatchItem]:
    url = "https://www.sports.ru/football/match/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    for item in soup.select('.stat-table.matches-table')[:limit]:
        time_tag = item.select('.gray-text')
        if len(time_tag) >= 2:
            time = f"{time_tag[0].get_text(strip=True)}"
            tournament = f"{time_tag[1].get_text(strip=True)}"
        else:
            time = f"{time_tag[0].get_text(strip=True)}"
            tournament = f"Не начался"

        name_tags = item.select('.player')
        if not name_tags:
            continue
        if len(name_tags) >= 2:
            teams = f"{name_tags[0].get_text(strip=True)} - {name_tags[1].get_text(strip=True)}"
        else:
            teams = name_tags[0].get_text(strip=True)

        score_left_tag = item.select_one('.s-left')
        score_left = score_left_tag.get_text(strip=True) if score_left_tag else "0"
        score_right_tag = item.select_one('.s-right')
        score_right = score_right_tag.get_text(strip=True) if score_right_tag else "0"
        score = f"{score_left} : {score_right}"
        link_tag = item.select_one('.score')
        link = f"https://www.sports.ru{link_tag['href']}" if link_tag and link_tag.has_attr('href') else '#'
        matches.append({
            'time': time,
            'teams': teams,
            'score': score if score else 'vs',
            'tournament': tournament,
            'link': link,
        })
    return matches


def _parse_eurofootball(limit: int = 5) -> List[MatchItem]:
    url = "https://www.euro-football.ru/online"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    for item in soup.select('.match-online-list__item')[:limit]:
        time_tag = item.select_one('.match-online-list__item-status')
        time = time_tag.get_text(strip=True) if time_tag else '?'
        team1name_tag = item.select_one('.team1name')
        home_team = team1name_tag.get_text(strip=True) if team1name_tag else " "
        team2name_tag = item.select_one('.team2name')
        away_team = team2name_tag.get_text(strip=True) if team2name_tag else " "
        score_tags = item.select('.goal-team-block')

        if len(score_tags) >= 2:
            score = f"{score_tags[0].get_text(strip=True) if score_tags[0].get_text(strip=True) else '0'} - {score_tags[1].get_text(strip=True) if score_tags[1].get_text(strip=True) else '0'}"
        else:
            score = 'vs'

        link_tag = item.select_one('.item-play-video__link')
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else '#'
        matches.append({
            'time': time,
            'teams': f"{home_team} - {away_team}",
            'score': score,
            'tournament': " ",
            'link': link,
        })
    return matches


def fetch_all_matches(limit: int = 5) -> Dict[str, List[MatchItem]]:
    return {
        'Championat.com': _parse_championat(limit),
        'Sports.ru': _parse_sportsru(limit),
        'Euro-Football.ru': _parse_eurofootball(limit),
    }
