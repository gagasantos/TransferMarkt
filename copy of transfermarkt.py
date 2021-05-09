import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
# import allclubs
# from allclubs import get_players  # calls function I created in separate file
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import string

urls = ['https://www.transfermarkt.us/premier-league/startseite/wettbewerb/GB1',
        'https://www.transfermarkt.us/la-liga/startseite/wettbewerb/ES1',
        'https://www.transfermarkt.us/serie-a/startseite/wettbewerb/IT1',
        'https://www.transfermarkt.us/1-bundesliga/startseite/wettbewerb/L1',
        'https://www.transfermarkt.us/ligue-1/startseite/wettbewerb/FR1']

headers = {'User-Agent':
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

# players = get_players()  # calls the list of tuples that contains each player's name, position and link

full_list = []

def get_clubs():  # Function iterates through list of Urls and collects link for each team.
    all_clubs = []
    for i in urls:
        session = requests.Session()
        # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
        retry = Retry(connect=3, backoff_factor=0.5)  # powerful request function that prevents accessing
        adapter = HTTPAdapter(max_retries=retry)  # page too many times and continues to try to get function and slows
        session.mount('http://', adapter)  # process down by .5x after each 3 failures
        session.mount('https://', adapter)

        tree = session.get(i, headers=headers)
        # tree = requests.get(i, headers=headers)

        results = BeautifulSoup(tree.content, 'lxml')

        teams_odd = results.find_all('tr', class_='odd')
        teams_even = results.find_all('tr', class_='even')
        c = []
        for i in teams_odd:  # collects href and stores it in list
            link = "https://www.transfermarkt.us" + i.find('a').get('href')
            c.append(link)
        c1 = c[:-6]

        for i in teams_even:  # collects href and stores it in list
            link = "https://www.transfermarkt.us" + i.find('a').get('href')
            c1.append(link)
        clubs = c1[:-4]
        all_clubs.extend(clubs)

    return all_clubs  # returns big list of every link


def get_players():
    all_clubs = get_clubs()
    all_players = []
    for i in all_clubs:  # iterates through every link and collects name and position
        url = i  # of every player within in link/team
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        tree = session.get(url, headers=headers)
        # tree = requests.get(i, headers=headers)
        results = BeautifulSoup(tree.content, 'lxml')

        players_odd = results.find_all('tr', class_='odd')
        players_even = results.find_all('tr', class_='even')

        p = []

        for i in players_odd:  # collects name, link, position and stores it in list
            link = "https://www.transfermarkt.us" + i.find('a', class_='spielprofil_tooltip').get('href')
            name = i.find('a', class_='spielprofil_tooltip').get_text()
            pos = i.find('td', class_='zentriert').get('title')
            p.append((name, link, pos))
            # print(p)

        for i in players_even:  # collects name, link, position and stores it in list
            link = "https://www.transfermarkt.us" + i.find('a', class_='spielprofil_tooltip').get('href')
            name = i.find('a', class_='spielprofil_tooltip').get_text()
            pos = i.find('td', class_='zentriert').get('title')
            p.append((name, link, pos))

        print(p[-1])
        all_players.extend(p)
    return all_players

def player_info(link):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    tree = session.get(link, headers=headers)
    results = BeautifulSoup(tree.content, 'lxml')
    p_data = results.find_all('div', class_='dataBottom')
    data = []
    if p_data:  # created if else function to prevent missing value to stop program
        for age in p_data:  # scans html data and finds all occasions of span.birthDate
            player_data = age.find_all('span', itemprop='birthDate')
            for age_1 in player_data:
                remove = string.punctuation  # https://machinelearningmastery.com/clean-text-machine-learning-python/
                play = age_1.get_text().translate(str.maketrans('', '', remove))
                play = play.strip()  # removes all random punctuation to extract clean value, resource above
                play = play[-2:]  # pulls age information
                data.append(play)

        for citizenship in p_data:
            nationality = citizenship.find('span', itemprop='nationality').get_text()
            data.append(nationality)  # looks for span.nationality and pulls birthplace

        for h in p_data:
            height = h.find_all('span', itemprop='height')
            if height:  # if else created to prevent missing code from breaking program
                for hh in height:
                    yes = hh.get_text()  # looks for all occurrences of span.height and pulls height
                    yes = yes.replace(",", ".")
                    data.append(yes[:4])
            else:
                yes = ['-']  # value to be added to list in case of missing value
                data.append(yes)
        return data
    else:
        data = ['-', '-', '-']  # value to be added to list in case of missing value
        return data


def game_statistics(link):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    tree = session.get(link, headers=headers)
    results = BeautifulSoup(tree.content, 'lxml')
    game_stats = results.find_all('table', class_='items')
    if game_stats:
        for a in game_stats:
            stats = a.find_all('td', class_="zentriert")
            goals_apps = []
            for s in stats:
                goals = s.get_text()
                goals_apps.append(goals)
            goals_apps = goals_apps[:5]

            # print(input("game stat checkpoint: "))
            return goals_apps
    else:
        goals_apps = ['-', '-', '-', '-', '-']
        return goals_apps


def transfer_value(link):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    tree = session.get(link, headers=headers)
    # tree = requests.get(link, headers=headers)
    results = BeautifulSoup(tree.content, 'lxml')
    t_stats = results.find_all('div', class_='marktwertentwicklung')
    if t_stats:
        for m in t_stats:
            transfer = m.find_all('div', class_="right-td")
            end_val = []
            for fee in transfer:
                remove = string.punctuation
                remove = remove.replace("~", "")
                remove = remove.replace('|', "")
                remove = remove.replace(".", "")
                value = fee.get_text().translate(str.maketrans('', '', remove))
                value = value.strip()
                value = value[:5]
                value = value[:2] + value[2:]
                end_val.append(value)
            end_val.pop(1)
            # print(input("transfer value checkpoint: "))
            return end_val
        # player.extend(end_val)
    else:
        end_val = ['-', '-']
        return end_val


def league(link):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    tree = session.get(link, headers=headers)
    # tree = requests.get(link, headers=headers)
    results = BeautifulSoup(tree.content, 'lxml')
    league_data = results.find_all('span', class_='mediumpunkt')
    team_data = results.find_all('span', class_='hauptpunkt')
    team_league = []
    if league_data:
        for i in league_data:
            league_name = i.find('img', class_='flaggenrahmen')
            if league_name:
                team_league.append(league_name.get('title'))
            else:
                league_name = ['-']
                team_league.append(league_name)
    else:
        league_name = ['-']
        team_league.append(league_name)
    if team_data:
        for i in team_data:
            team_name = i.find('a').get_text()
            team_league.append(team_name)
    else:
        team_name = ['-']
        team_league.append(team_name)
    return team_league


def nat_team(link):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    tree = session.get(link, headers=headers)
    # tree = requests.get(link, headers=headers)
    results = BeautifulSoup(tree.content, 'lxml')
    # return 1
    n_stats = results.find_all('table', class_='borderloser_odd_even_style')

    if n_stats:
        for i in n_stats:
            team = i.find('td', class_='hauptlink').get_text()
            team = [team.strip()]
            # print(input("national team checkpoint: "))
            return team
    else:
        team = ['-']
        return team

        # player.extend(team)


def nat_stat(link):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    tree = session.get(link, headers=headers)
    # tree = requests.get(link, headers=headers)
    results = BeautifulSoup(tree.content, 'lxml')
    n_stats = results.find_all('table', class_='borderloser_odd_even_style')

    if n_stats:
        for i in n_stats:
            nat_stats = []
            nat = i.find_all('td', class_="zentriert")
            for s in nat:
                nat_text = s.get_text()
                nat_text = nat_text.strip()
                nat_stats.append(nat_text)
                # print(input("national team stats checkpoint: "))
            nat_stats = nat_stats[3:5]
            return nat_stats
    else:
        nat_stats = ['-', '-']
        return nat_stats

        # player.extend(nat_stats)


df_header = ['Name', 'Position', 'Age', 'Nationality', 'Height (m)',
             'Apps', 'Goals', 'Assists',
             'Minutes/Goal', 'Minutes Played',
             'C.V alue', 'H.Value',
             'League', 'Team', 'N.Team', 'N.Apps', 'N.Goals']
# Created list of column names to be plugged into DataFrame
players = get_players()

for i in players:  # for loop iterates through list of tuples
    player = [i[0], i[2]]  # collects players name and position
    player.extend(player_info(i[1]))  # collects info such as height and nationality calling function above
    player.extend(game_statistics(i[1]))  # collects goals and assists calling function above
    player.extend(transfer_value(i[1]))  # calls function above and collects transfer information
    player.extend(league(i[1]))  # calls function league(link) and gives league information
    player.extend(nat_team(i[1]))  # calls nat_team(link) and gives national team level
    player.extend(nat_stat(i[1]))  # calls nat_stat(link) and gives stats from national team level
    #  all of these function are extended to list player, creating a row for each individual player
    full_list.append(player)  # each list is added to full_list list
    print(len(full_list))  # prints length of list which helps determine progress of list
    df = DataFrame(full_list, columns=df_header)  # takes list of lists and creates DataFrame
    df.to_excel(r'C:\Users\gworkman\Documents\School\transfermarkt.xlsx', index=False)
    #  every iteration writes results into an excel file

print(df.head())  # prints top 5 rows of result
