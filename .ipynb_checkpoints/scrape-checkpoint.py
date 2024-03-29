from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import time
import pandas as pd
import datetime
import json
import os

def download_data(con, month, day, year):
    try:
        games_data = get_data_from_date(month, day, year)
        save_to_db(con, games_data)
    except:
        return(None)

def random_proxy(proxies):
    return random.randint(0, len(proxies) - 1)
    
def open_with_proxy(u, initial_proxy = {'ip': '176.98.95.105', 'port': '32018'}
, max_tries = 20):
    ua = UserAgent() # From here we generate a random user agent
    proxies = [] # Will contain proxies [ip, port]

    # Retrieve latest proxies
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')
    soup = BeautifulSoup(proxies_doc, 'html.parser')
    # proxies_table = soup.find(id='proxylisttable')
    proxies_table = soup.find('table', {'class': 'table-striped'})
  # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string,
            'country': row.find_all('td')[3].string
      })
        
    #print(proxies)

    connected = False
    num_tries = 1

    while connected is False:
        # Generate a random proxy
        if num_tries == 0:
            proxy = initial_proxy
        else:
            proxy_index = random_proxy(proxies)
            proxy = proxies[proxy_index]
        # print(proxy)
        num_tries += 1
    
        req = Request(u)
        req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')

        try:
            html = urlopen(req).read().decode('utf8')
            connected = True
            print('Connected with ' + str(num_tries) + ' tries')
            with open('good_proxies.txt', 'a') as f:
                f.write(json.dumps(proxy) + '\n')
            return(html)
        except: # If error, delete this proxy and find another one
            del proxies[proxy_index]
            if num_tries > max_tries:
                print('Unable to connect. Max tries reached')
                return(None)

def get_stat_from_tr(tr):
    return([tr.find('th')['csk'], dict([(x['data-stat'], x.text) for x in tr.find_all('td')])])

#def get_sql_connection():
#    import sqlalchemy
#    import json
#    with open('config.json') as f:
#        config = json.load(f)
#        
#    database_username = config.get('db_username')
#    database_password = config.get('db_password')
#    database_ip       = config.get('db_ip')
#    database_name     = config.get('db_name')
#    database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
#                                                   format(database_username, database_password, 
#                                                          database_ip, database_name))
#    return(database_connection)

def fluff_number(x, digits = 2):
    y = str(x)
    gap = digits - len(str(x))
    if gap > 0:
        for i in range(gap):
            y = '0' + y
    return(y)

#def save_to_db(con, df):
#    df.to_sql(con=con, name='nba_games_players', 
#              if_exists = 'append', index = False)    
def get_games_from_date(month, day, year):
    site_url = 'http://www.basketball-reference.com'
    u = site_url + '/boxscores/?'
    u += 'month=' + fluff_number(month)
    u += '&day=' + fluff_number(day)
    u += '&year=' + str(year)
    #print(u)
    html = open_with_proxy(u)
    soup = BeautifulSoup(html, 'html.parser')
    links = [site_url + x['href'] for x in soup.find_all('a', text = 'Box Score')]
    #print(links)
    return(links)

def get_table_from_game(u):
    game_name = u.split('/')[-1].split('.')[0]
    print(game_name) # Works
    time_to_sleep = random.randint(2,8)
    time.sleep(time_to_sleep)
    #print(u)
    html = open_with_proxy(u)
    #print(html)

    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table', attrs={'class': 'stats_table'})
    #print(tables)
    table_tuples = [(tbl['id'].split('-')[1], [tr for tr in tbl.find_all('tr') if tr.find('th').has_attr('csk')]) for tbl in tables if tbl['id'].split('-')[-2] == 'game' and tbl['id'].split('-')[-1] in ['basic', 'advanced']]
    data = [(tbl_tup[0], [get_stat_from_tr(tr) for tr in tbl_tup[1]]) for tbl_tup in table_tuples]
    d = {}
    print(len(data))
    for tbl in data:
        #print(tbl)
        team = tbl[0]
        for player in tbl[1]:
            player_name = player[0]
            # print(player[1])
            if player_name in d.keys():
                # Merge 
                d[player_name] = {**d.get(player_name), **player[1]}
            else:
                # initialize
                d[player_name] = {**{'team': team, 'game': game_name}, **player[1]}
    df = pd.DataFrame(d).T
    #print(d)
    return(df)

def get_data_from_date(month, day, year):
    games = get_games_from_date(month, day, year)
    data_list = [get_table_from_game(game) for game in games]
    print(data_list)
    data = pd.concat(data_list)
    #print(data)
    data['year'] = year
    data['month'] = month
    data['day'] = day
    data['date'] = str(year) + '-' + fluff_number(month) + '-' + fluff_number(day)
    data['player'] = data.index
    # print(data)
    # data = data.set_index(['game', 'player'])
    return(data)

def download_data_csv(data_path, month, day, year):
    file_path = data_path + 'game' + str(year) + '_' + fluff_number(month) + '_' + fluff_number(day) + '.csv.gz'
    if os.path.exists(file_path) == False:
        try:
            games_data = get_data_from_date(month, day, year)
            print(games_data)
            # print(games_data)
            games_data.to_csv(file_path, index = False, compression = 'gzip')
            # print(file_path)
            # print('Finished Saving -- hooray')
        except:
            return(None)
    else:
        print('Already downloaded. Moving on.')
        return(None)

def main():
    data_path = 'data/'
    
    # create the data subpath if doesn't already exist
    if not os.path.exists(data_path):
        os.mkdir(data_path)

    numdays = 365 * 3
    base = datetime.date.today()
    # base = datetime.date(2018,3,3)
    date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
    dates = [(x.month, x.day, x.year) for x in date_list]
    
    for x in dates:
        print(x)
        # Save data to a SQL database
        #download_data(con, x[0], x[1], x[2])

        # Instead, save to a CSV
        download_data_csv(data_path, x[0], x[1], x[2])
    
if __name__ == '__main__':
#    con = get_sql_connection()
    main()
