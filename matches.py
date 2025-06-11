from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

from config import HEADERS


MatchItem = Dict[str, str]


def _parse_sportsru(limit: int = 15) -> List[MatchItem]:
    url = "https://www.sports.ru/stat/football/center/today/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    for match in soup.select('.stat-results__row')[:limit]:
        time = match.select_one('.stat-results__time')
        time = time.get_text(strip=True) if time else "?"
        teams = match.select('.stat-results__team-name')
        if len(teams) < 2:
            continue
        home_team = teams[0].get_text(strip=True)
        away_team = teams[1].get_text(strip=True)
        score = match.select_one('.stat-results__count')
        score = score.get_text(strip=True) if score else 'vs'
        tournament = match.select_one('.stat-results__tournament')
        tournament = tournament.get_text(strip=True) if tournament else ''
        link = match.find('a')
        link = f"https://www.sports.ru{link['href']}" if link and link.has_attr('href') else '#'
        matches.append({
            'time': time,
            'teams': f"{home_team} - {away_team}",
            'score': score,
            'tournament': tournament,
            'link': link,
        })
    return matches


def _parse_championat(limit: int = 15) -> List[MatchItem]:
    url = "https://www.championat.com/football/_live.html"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    for row in soup.select('.live-match-item')[:limit]:
        time_tag = row.select_one('.match-time')
        time = time_tag.get_text(strip=True) if time_tag else '?'
        teams = row.select('.team-name')
        if len(teams) < 2:
            continue
        home_team = teams[0].get_text(strip=True)
        away_team = teams[1].get_text(strip=True)
        score = row.select_one('.match-score')
        score = score.get_text(strip=True) if score else 'vs'
        tournament = row.select_one('.tournament')
        tournament = tournament.get_text(strip=True) if tournament else ''
        link_tag = row.find('a')
        link = f"https://www.championat.com{link_tag['href']}" if link_tag and link_tag.has_attr('href') else '#'
        matches.append({
            'time': time,
            'teams': f"{home_team} - {away_team}",
            'score': score,
            'tournament': tournament,
            'link': link,
        })
    return matches


def _parse_eurofootball(limit: int = 15) -> List[MatchItem]:
    url = "https://www.euro-football.ru/live"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    for row in soup.select('.match-item')[:limit]:
        time_tag = row.select_one('.match-item-time')
        time = time_tag.get_text(strip=True) if time_tag else '?'
        teams = row.select('.match-item-team')
        if len(teams) < 2:
            continue
        home_team = teams[0].get_text(strip=True)
        away_team = teams[1].get_text(strip=True)
        score = row.select_one('.match-item-score')
        score = score.get_text(strip=True) if score else 'vs'
        tournament = row.select_one('.match-item-tournament')
        tournament = tournament.get_text(strip=True) if tournament else ''
        link_tag = row.find('a')
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else '#'
        matches.append({
            'time': time,
            'teams': f"{home_team} - {away_team}",
            'score': score,
            'tournament': tournament,
            'link': link,
        })
    return matches


def _parse_espn(limit: int = 15) -> List[MatchItem]:
    """Parse live matches from ESPN public API."""
    today = datetime.utcnow().strftime('%Y%m%d')
    url = f"https://site.api.espn.com/apis/v2/sports/soccer/scoreboard?dates={today}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
    except Exception:
        return []
    matches: List[MatchItem] = []
    for event in data.get('events', [])[:limit]:
        competition = event.get('name', '')
        link = event.get('link', '#')
        comps = event.get('competitions', [])
        if not comps:
            continue
        c0 = comps[0]
        status = c0.get('status', {}).get('type', {}).get('shortDetail', '')
        competitors = c0.get('competitors', [])
        if len(competitors) < 2:
            continue
        home = competitors[0]
        away = competitors[1]
        home_team = home.get('team', {}).get('shortDisplayName', '?')
        away_team = away.get('team', {}).get('shortDisplayName', '?')
        score_home = home.get('score', '')
        score_away = away.get('score', '')
        matches.append({
            'time': status,
            'teams': f"{home_team} - {away_team}",
            'score': f"{score_home}:{score_away}" if score_home else 'vs',
            'tournament': competition,
            'link': link,
        })
    return matches


def fetch_all_matches(limit: int = 15) -> Dict[str, List[MatchItem]]:
    return {
        'Sports.ru': _parse_sportsru(limit),
        'Championat': _parse_championat(limit),
        'Euro-Football': _parse_eurofootball(limit),
        'ESPN': _parse_espn(limit),
    }
