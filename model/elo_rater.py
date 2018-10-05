# attempt to implement elo rater with dataclasses and the standard library

import csv
import datetime
import os
from dataclasses import dataclass, field

print('')
print('++ start ++')

GRADE = 'BReserves'
YEAR = 2018
DATA_PATH = os.getcwd() + '/data/test/'


def get_grades_years():

    files_list = []
    for file in os.listdir():
        file_name, file_ext = os.path.splitext(file)
        if file_name == 'README':
            continue  # skip any README files
        grade, year, data_type = tuple(file_name.split('_'))
        file_list.append((grade, year, file_type))

    files_tuple = tuple(sorted(file_list))

    return files_tuple


def get_games(csv_filename):

    results_list = []
    index = 0

    with open(DATA_PATH + csv_filename) as csvfile:
        results_dictreader = csv.DictReader(csvfile)

        for result in results_dictreader:
            results_list.append(dict(result))

    results_tuple = tuple(results_list)

    return results_tuple


@dataclass
class Season:
    year: int
    grade: str
    teams: tuple = field(init=False)

    def __post_init__(self):
        self.teams = self.initalise_teams()

    WIN_POINTS = 2
    DRAW_POINTS = 1

    def initalise_teams(self):
        teams = []

        with open(DATA_PATH + self.results) as csvfile:
            results_csv = csv.DictReader(csvfile)
            for game in results_csv:
                team_home = game.get('team_home')
                if team_home.lower() != 'bye':
                    teams.append(Team(team_home))
                team_away = game.get('team_away')
                if team_away.lower() != 'bye':
                    teams.append(Team(team_away))
        teams = set(teams)
        return tuple(teams)

    @property
    def results(self):
        return f'{self.grade}_{self.year}_results.csv'

    @property
    def standings(self):

        standings = []
        team_value = {}
        for team in self.teams:
            team_value[team] = [team.points + 0.1 * team.runs_percentage]

        while len(team_value) > 0:
            max_team = max(team_value.keys(), key=(lambda k: team_value[k]))
            standings.append(max_team)
            team_value.pop(max_team)

        return tuple(standings)

    @staticmethod
    def filter_byes(name):
        pass

    def print_season_info(self):
        print(self.grade, self.year)

    def print_standings(self):

        print('-')
        self.print_season_info()
        print('-')
        print('TEAM', '\t\t', 'POINTS', 'R%', 'ELO', 'WINS', 'LOSSES', 'DRAWS', sep='\t')
        for team in self.standings:
            Team.print_team(team)
        print('-')

    @staticmethod
    def get_team_from_name_string(teams, team_name_string):
        for team in teams:
            if team.name == team_name_string:
                return team


@dataclass
class Game:
    team_home: str
    team_away: str  # should these be the Team object themselves?
    score_home: int
    score_away: int
    date_time: str = None
    round_number: int = None
    ground: str = None
    is_final: bool = None
    # type of game - future / results - prediction

    @classmethod
    def from_dict(cls, game_dict):
        '''Take the dictionary returned from reading the csv and turn it into the game object'''
        '''Ideally this will be able to handle some degree of dirtiness or incompletion in the data'''

        team_home = Season.get_team_from_name_string(season.teams, game_dict['team_home'])
        team_away = Season.get_team_from_name_string(season.teams, game_dict['team_away'])
        score_home = int(game_dict['score_home'])
        score_away = int(game_dict['score_away'])
        date_time = game_dict['date_time']
        # Game.try_key(game_dict, 'ground')
        # ground = game_dict['ground']
        # round_number = game_dict['round_number']
        print(type(team_home))
        return cls(team_home, team_away, score_home, score_away, date_time)

    @staticmethod
    def try_key(dict, key):
        try:
            return dict[key]
        except KeyError:
            print(f'THERE\'S NO \'{key}\' IN THE DICTIONARY')
            return None

    # def winner_loser():

    def run_recorder(self):
        # I need to set the team_home attribute to be the Team object in Season.teams referenced by the Team.name string found in the results csv.

        self.team_home.runs_scored += self.score_home
        self.team_home.runs_allowed += self.score_away
        self.team_away.runs_scored += self.score_away
        self.team_away.runs_allowed += self.score_home

        # print(self.team_home.runs_scored)
        # definitely adding it to the object...


# @dataclass
# class CompletedGame(Game):
#     score_home: int
#     score_away: int
#     pass
#
#
# @dataclass
# class FutureGame(Game):
#     win_prob_home: float
#     pass
#
#     @property
#     def win_prob_home(self):
#         return exp_val_home
#
#     @property
#     def win_prob_away(self):
#         return 1 - self.win_prob_home


@dataclass(unsafe_hash=True)
class Team:
    name: str
    colours: tuple = 'NaN'
    runs_scored: int = 0
    runs_allowed: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    elo: float = field(init=False)

    def __post_init__(self):
        self.elo = self.initalise_elo()

    def get_previous_standings(self):
        try:
            with open(DATA_PATH + f'{GRADE}_{YEAR - 1}_standings.csv') as csvfile:
                previous_standings = csv.DictReader(csvfile)
                return previous_standings
        except FileNotFoundError:
            return None

    def initalise_elo(self):
        if not self.is_returning:
            return 1500
        else:
            with open(DATA_PATH + f'{GRADE}_{YEAR - 1}_standings.csv') as csvfile:
                previous_standings = csv.DictReader(csvfile)
                for row in previous_standings:
                    if row.get('name') == self.name:
                        return self.regress_elo(row.get('elo'))

    @property
    def is_returning(self):
        is_returning = False
        try:
            with open(DATA_PATH + f'{GRADE}_{YEAR - 1}_standings.csv') as csvfile:
                previous_standings = csv.DictReader(csvfile)
                for row in previous_standings:
                    if row.get('name') == self.name:
                        is_returning = True
        except FileNotFoundError:
            print('File Not Found')
            print(os.getcwd())

        return is_returning

    @property
    def played(self):
        return self.wins + self.losses + self.draws

    @property
    def points(self):
        return self.wins * Season.WIN_POINTS + self.draws * Season.DRAW_POINTS

    @property
    def runs_percentage(self):
        return self.calc_stat_percent(up=self.runs_scored, down=self.runs_allowed)

    @property
    def win_percentage(self):
        return self.calc_stat_percent(up=self.wins, down=self.losses)

    @staticmethod
    def regress_elo(elo):
        return float(elo) / 2 + 750  # regress elo halfway to the mean

    @staticmethod
    def calc_stat_percent(up, down):
        try:
            return 0.500 + 0.500 * ((up - down) / (up + down))
        except ZeroDivisionError:
            return 0.500

    def print_team(self):
        print(self.name.upper(), ' ' * (23 - len(self.name)), self.points,
              f'{round(self.runs_percentage, ndigits=3)}',
              f'{round(self.elo)}', self.wins, self.losses, self.draws, sep='\t')

    def predict_next_game(self):
        pass


season = Season(YEAR, GRADE)
for team in season.teams:
    print(team)


def parse_game():
    Game.run_recorder()


for game_dict in get_games(season.results):
    game = Game.from_dict(game_dict)
    print(game.team_home.name, game.score_home, game.score_away, game.team_away.name)
    Game.run_recorder(game)

Season.print_standings(season)

for team in season.teams:
    print(team)


print('++ done ++')
