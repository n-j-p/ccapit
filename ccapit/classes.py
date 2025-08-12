import requests
import re

class Player():
    def __init__(self, player_name, my_chess_com_id, my_email, session = None):
        self.headers = f"{{'User-Agent':'username: {my_chess_com_id}, email: {my_email}'}}"
  
        self.player_name = player_name
        if session is None:
            session = requests.Session()
        self.session = session

        self.base_url = f'https://api.chess.com/pub/player/{player_name}'
        self.stats_url = self.base_url + '/stats'
        self.archives_url = self.base_url + '/games/archives'
        with self.session.get(self.base_url, headers=self.headers) as base_info:
            self.base_info = base_info.json()
        try:
            self.name = self.base_info['name']
        except KeyError:
            self.name = ''
        self.username = self.base_info['username']
        country_pattern = re.compile(r'/country/(\w+)')
        try:
            self.country = country_pattern.search(self.base_info['country']).group(1)
        except Exception:
            self.country = ''
    def get_all_ratings(self):
        with self.session.get(self.stats_url, headers=self.headers) as stats_info:
            self.stats_info = stats_info.json()
        self.stats = {}
        for game_format in self.stats_info.keys():
            #print(game_format)
            try:
                self.stats[game_format] = self.stats_info[game_format]['last']['rating']
            except KeyError:
                continue
            except TypeError: # fide, etc. is just an integer
                self.stats[game_format] = self.stats_info[game_format]
            self.stats[game_format] = int(self.stats[game_format])

    def _get_active_months(self):
        with self.session.get(self.archives_url, headers=self.headers) as archives_info:
            self.archives_info = archives_info.json()
        
        monthly_archives_pattern = re.compile(r'/games/(\d+)/(\d+)')
        yearmons = [(int(v.group(1)), int(v.group(2))) for v in \
                    [monthly_archives_pattern.search(x) for x in \
                         self.archives_info['archives']] if v]
        self.active_months = yearmons

    def game_generator(self, time_class = 'blitz',
                       rules = 'chess'):
        try:
            active_months = self.active_months
        except AttributeError:
            self._get_active_months()
            active_months = self.active_months
        for YM in active_months[::-1]:
            monthly_games_url =  self.base_url + f'/games/{YM[0]}/{YM[1]:02d}'
            with self.session.get(monthly_games_url, headers=self.headers) as monthly_games:
                games = monthly_games.json()['games']
                for game in games[::-1]:
                    if game['rules'] == rules and \
                       game['time_class'] == time_class:
                        yield game
                        
                        #yield tx.split('\n\n')[0]
