# KBO Website Crawling
# Involves HTTP Parser from https://statiz.sporki.com/team/?m=seasonOrder&t_code=3001&year=2024
import requests
from bs4 import BeautifulSoup
import pandas as pd

from enum import Enum


KBO_TEAM_URL = "https://statiz.sporki.com/team"
KBO_PLAYER_URL = "https://statiz.sporki.com/player"


class KBOTeams(Enum):
    SAMSUNG_LIONS = 1001
    KIA_TIGERS = 2002
    LOTTE_GIANTS = 3001
    LG_TWINS = 5002
    DOOSAN_BEARS = 6002
    HANHWA_EAGLES = 7002
    SSG_LANDERS = 9002
    KIWOOM_HEROS = 10001
    NC_DINOS = 11001
    KT_WIZS = 12001


def parse_team_member(htmls: str):
    soup = BeautifulSoup(htmls, 'lxml')
    player_div = soup.find('div', class_='back_number_area')

    # Extract all player names and their IDs
    players = []
    for item in player_div.find_all('a', href=True):
        # Extract player name and ID from the anchor tag
        player_name = item.text.strip()
        player_id = item['href'].split('p_no=')[-1]  # Extract the player ID from the URL
        players.append({'player_id': player_id, 'player_name': player_name})

    # Convert the list of players to a pandas DataFrame
    df_players = pd.DataFrame(players)
    return df_players


def parse_player_info(htmls: str):
    soup = BeautifulSoup(htmls, 'lxml')
    table = soup.find('div', class_="table_type02 transverse_scroll").find('table')

    # Split table sections based on alternating <th> and <td> structure
    sections = []
    current_headers = []
    current_rows = []

    # Loop through all rows in the table
    for row in table.find_all('tr'):
        # If row has <th>, it's a new section header
        if row.find_all('th'):
            # If there's a previous section, store it
            if current_headers and current_rows:
                sections.append((current_headers, current_rows))
                current_headers = []
                current_rows = []
            # Collect headers for the new section
            current_headers = [th.text.strip() for th in row.find_all('th')]
        
        # If row has <td>, it's a data row
        if row.find_all('td'):
            current_rows.append([td.text.strip() for td in row.find_all('td')])

    # Append the final section
    if current_headers and current_rows:
        sections.append((current_headers, current_rows))

    # Convert each section to a DataFrame
    dataframes = []
    for headers, rows in sections:
        df = pd.DataFrame(rows, columns=headers)
        dataframes.append(df)

    return dataframes


def request_team_members(team: KBOTeams, year: int):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    param = {
        "m": "seasonBacknumber",  # Get the team members list from season Back number
        "t_code": team.value,  # Team code from Enum
        "year": year
    }

    resp = requests.get(KBO_TEAM_URL, params=param, headers=header)
    
    if resp.status_code == 200:
        result = parse_team_member(resp.text)
        resp.close()
        return result
    else:
        RuntimeError(resp.status_code)


def request_player_info(player_id: int):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    
    param = {
        'm': 'situation',
        'p_no': player_id,
    }

    resp = requests.post(KBO_PLAYER_URL, params=param, headers=header)
    if resp.status_code == 200:
        result = parse_player_info(resp.text) 
        resp.close()
        return result
    else:
        RuntimeError(resp.status_code)
