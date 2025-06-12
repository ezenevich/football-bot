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
        name_tag = item.select_one('.team-name')
        result_tag = item.select_one('.livetable-event__result')
        status_tag = item.select_one('.livetable-event__status')
        if not name_tag:
            continue
        link_tag = item.find('a')
        link = link_tag['href']
        matches.append({
            'time': date_tag.get_text(strip=True) if date_tag else '?',
            'teams': name_tag.get_text(strip=True),
            'score': result_tag.get_text(strip=True) if result_tag else 'vs',
            'tournament': status_tag.get_text(strip=True) if status_tag else '',
            'link': f"https://www.championat.com{link}" if link.startswith('/') else link,
        })
    return matches


def _parse_sportsru(limit: int = 5) -> List[MatchItem]:
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





def _parse_eurofootball(limit: int = 5) -> List[MatchItem]:
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


def _parse_matchtv(limit: int = 15) -> List[MatchItem]:
    """Parse matches from Match TV's match center."""
    url = "https://matchtv.ru/match-center"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    matches: List[MatchItem] = []
    container = soup.select_one("div.mc-tab-content")
    if not container:
        return matches
    for row in container.find_all("div", recursive=False)[:limit]:
        time_tag = row.select_one(".time, .mc-match__time")
        time = time_tag.get_text(strip=True) if time_tag else "?"
        teams = row.select(".team, .mc-match__team-name")
        if len(teams) < 2:
            continue
        home_team = teams[0].get_text(strip=True)
        away_team = teams[1].get_text(strip=True)
        score_tag = row.select_one(".score, .mc-match__score")
        score = score_tag.get_text(strip=True) if score_tag else "vs"
        tournament_tag = row.select_one(".tournament, .mc-match__tournament")
        tournament = tournament_tag.get_text(strip=True) if tournament_tag else ""
        link_tag = row.find("a")
        link = link_tag["href"] if link_tag and link_tag.has_attr("href") else "#"
        matches.append({
            "time": time,
            "teams": f"{home_team} - {away_team}",
            "score": score,
            "tournament": tournament,
            "link": link,
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


def _parse_football_data_api(limit: int = 15) -> List[MatchItem]:
    """Fetch matches from football-data.org API if a token is provided."""
    if not FOOTBALL_DATA_TOKEN:
        return []
    today = datetime.utcnow().strftime('%Y-%m-%d')
    url = (
        'https://api.football-data.org/v4/matches'
        f'?dateFrom={today}&dateTo={today}'
    )
    headers = {'X-Auth-Token': FOOTBALL_DATA_TOKEN}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
    except Exception:
        return []
    matches: List[MatchItem] = []
    for m in data.get('matches', [])[:limit]:
        utc = m.get('utcDate', '?')
        tournament = m.get('competition', {}).get('name', '')
        home = m.get('homeTeam', {}).get('shortName', '?')
        away = m.get('awayTeam', {}).get('shortName', '?')
        full_time = m.get('score', {}).get('fullTime', {})
        home_score = full_time.get('home')
        away_score = full_time.get('away')
        match_id = m.get('id')
        matches.append({
            'time': utc,
            'teams': f"{home} - {away}",
            'score': (
                f"{home_score}:{away_score}"
                if home_score is not None and away_score is not None
                else 'vs'
            ),
            'tournament': tournament,
            'link': (
                f"https://www.football-data.org/match/{match_id}"
                if match_id else '#'
            ),
        })
    return matches


def fetch_all_matches(limit: int = 15) -> Dict[str, List[MatchItem]]:
    return {
        'Championat.com': _parse_championat(limit),
        # 'Sports.ru': _parse_sportsru(limit),
        # 'Euro-Football': _parse_eurofootball(limit),
        # 'Match TV': _parse_matchtv(limit),
        # 'ESPN': _parse_espn(limit),
        # 'Football-Data': _parse_football_data_api(limit),
    }
