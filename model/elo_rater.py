# attempt to implement elo rater with dataclasses and the standard library

import csv
import datetime
import os
import time
from dataclasses import dataclass, field

print()
print('++ start ++')

GRADE = 'BReserves'
YEAR = 2018
ROOT_PATH = os.getcwd()
DATA_PATH = ROOT_PATH + '/data/data_vsl/'


def get_grades_years():

    os.chdir(DATA_PATH)

    files_list = []
    for file in os.listdir():
        file_name, file_ext = os.path.splitext(file)
        if file_name == 'README':
            continue  # skip any README files

        grade, year, data_type = tuple(file_name.split('_'))

        if data_type == 'standings' or data_type == 'fixture':
            continue

        files_list.append((grade, year, data_type))

    files_tuple = tuple(sorted(files_list))

    os.chdir(ROOT_PATH)

    return files_tuple


def get_games(csv_filename):

    results_list = []

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

        with open(f'{DATA_PATH}{self.results}') as csvfile:
            results_csv = csv.DictReader(csvfile)
            for game in results_csv:
                team_home = game.get('team_home')
                if type(team_home) == str and team_home.lower() != 'bye':
                    teams.append(Team(team_home, self.grade, int(self.year)))
                team_away = game.get('team_away')
                if type(team_away) == str and team_away.lower() != 'bye':
                    teams.append(Team(team_away, self.grade, int(self.year)))
        teams = set(teams)
        return tuple(teams)

    @property
    def results(self):
        return f'{self.grade}_{self.year}_results.csv'

    @property
    def standings(self):

        standings = self.teams
        rank_string = 'win_percentage - wins - losses - draws - runs_scored - runs_allowed'
        rank_order = rank_string.split(' - ')

        for attribute in reversed(rank_order):  # sort from the least important to most important ranking
            standings = sorted(standings, key=lambda team: getattr(team, attribute), reverse=True)

        return tuple(standings)

    @property
    def longest_name(self):
        return max(len(team.name) for team in self.teams)

    @staticmethod
    def filter_byes(name):
        pass

    def print_season_info(self):
        print(self.grade, self.year)

    def print_standings(self):

        print('-')
        self.print_season_info()
        print('-')
        print('TEAM', ' ' * (self.longest_name - 5), 'W%', 'ELO', 'WINS', 'LOSSES', 'DRAWS', sep='\t')
        for team in self.standings:
            Team.print_team(team)
        print('-')

    def write_standings_csv(self):
        all_teams = []
        for team in self.standings:
            all_teams.append(team.__dict__)
            fieldnames = team.__dict__.keys()

        with open(f'{DATA_PATH}{grade}_{year}_standings.csv', 'w') as csvfile:
            standings_writer = csv.DictWriter(csvfile, fieldnames)
            standings_writer.writeheader()
            for team in all_teams:
                standings_writer.writerow(team)

    def predict_next_round(self):
        expected_value()

        # pass some teams in

        # perhaps use the fixture?
        # round_number of the current results. The some of the results files already have bye results inputted

        # find the next game the team is playing in
        # find the opposing team
        # get the elos of the teams and derive the expected values from there
        # remove the team from the list of teams.
        # return the expected value * 100 predicting the outcome

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
        try:
            score_home = int(game_dict['score_home'])
            score_away = int(game_dict['score_away'])
        except ValueError:
            print('Game results not found - please check output file')
            score_home = 0
            score_away = 0
        date_time = game_dict['date_time']
        # Game.try_key(game_dict, 'ground')
        # ground = game_dict['ground']
        # round_number = game_dict['round_number']
        if team_away is None or team_home is None:
            return None
        return cls(team_home, team_away, score_home, score_away, date_time)

    @staticmethod
    def try_key(dict, key):
        try:
            return dict[key]
        except KeyError:
            print(f'THERE\'S NO \'{key}\' IN THE DICTIONARY')
            return None

    @property
    def is_draw(self):

        if self.score_home == self.score_away:
            return True
        else:
            return False

    @property
    def winner(self):

        if self.score_home > self.score_away:
            return self.team_home
        elif self.score_away > self.score_home:
            return self.team_away
        else:
            return None

    @property
    def loser(self):

        if self.score_home > self.score_away:
            return self.team_away
        elif self.score_away > self.score_home:
            return self.team_home
        else:
            return None

    def get_actual_value_home(self):

        if self.team_home == self.winner:
            return 1
        elif self.is_draw:
            return 0.5
        else:
            return 0

    def record(self):

        self.team_home.runs_scored += self.score_home
        self.team_home.runs_allowed += self.score_away
        self.team_away.runs_scored += self.score_away
        self.team_away.runs_allowed += self.score_home

        if self.is_draw:
            self.team_home.draws += 1
            self.team_away.draws += 1
        else:
            self.winner.wins += 1
            self.loser.losses += 1


@dataclass(unsafe_hash=True)
class Team:
    name: str
    grade: str
    year: int
    colours: tuple = 'NaN'
    runs_scored: int = 0
    runs_allowed: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    elo: float = field(init=False)
    predicted_elo: float = field(init=False)

    def __post_init__(self):
        self.elo = self.initalise_elo()
        self.predicted_elo = self.initalise_elo()

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
            with open(DATA_PATH + f'{self.grade}_{self.year - 1}_standings.csv') as csvfile:
                previous_standings = csv.DictReader(csvfile)
                for row in previous_standings:
                    if row.get('name') == self.name:
                        return self.regress_elo(row.get('elo'))

    @property
    def is_returning(self):
        is_returning = False
        try:
            with open(DATA_PATH + f'{self.grade}_{self.year - 1}_standings.csv') as csvfile:
                previous_standings = csv.DictReader(csvfile)
                for row in previous_standings:
                    if row.get('name') == self.name:
                        is_returning = True
        except FileNotFoundError:
            # print('File Not Found: No previous season on record')
            pass

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

        print(self.name, ' ' * (season.longest_name - len(self.name)),
              f'\t{round(self.win_percentage, ndigits=3)}\t{round(self.elo)}\t',
              f'{self.wins}\t{self.losses}\t{self.draws}')


def calculate_expected_value_home(game):

    elo_home = game.team_home.elo
    elo_away = game.team_away.elo

    exp_val_home = 1 / (1 + 10**((elo_away - elo_home) / 400))

    # helpfully, the expected value is also the win probability for the given team.

    return exp_val_home


def calculate_elo(game, k=50):

    exp_val_home = calculate_expected_value_home(game)
    act_val_home = Game.get_actual_value_home(game)

    exp_val_away = 1 - exp_val_home
    act_val_away = 1 - act_val_home

    elo_home_new = game.team_home.elo + k * (act_val_home - exp_val_home)
    elo_away_new = game.team_away.elo + k * (act_val_away - exp_val_away)

    game.team_home.elo = elo_home_new
    game.team_away.elo = elo_away_new


def track_elo():
    # dictionary of team name keys with elo values. Ideally could work across seasons?
    pass


seasons = get_grades_years()
print(seasons)

for season in seasons:
    grade, year, data_type = season
    # if year == '2019' or grade != 'Division4East':
    #     continue
    season = Season(year, grade)
    print()
    # to filter the grades
    for game_dict in get_games(season.results):
        game = Game.from_dict(game_dict)
        if game is None:
            continue  # don't process games that don't have a valid team
            # this seems to be mostly Bye games - this filter should be improved in the official status log.
        Game.record(game)
        calculate_elo(game)
        track_elo()

    for team in season.teams:
        if not team.is_returning:
            print(team.name.upper())

    Season.write_standings_csv(season)

    Season.print_standings(season)

# need to write a x_x_standings.csv writer
# need to scrape the fixture for the home and away season
# maybe club objects would be useful after all...
# need to filter out seasons without sensible data (i.e. blank data)
# ideally output something that can feed directly into my website page - probably a graph is the simplest.
# additional web features are further away...


print('++ done ++')
