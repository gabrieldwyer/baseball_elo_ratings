# attempt to implement elo rater with dataclasses and the standard library
import csv
import datetime
import os
import random
import re
import time

from dataclasses import dataclass, field

import matplotlib.pyplot as plt

CURRENT_YEAR = '2019'
ROOT_PATH = os.getcwd()
MWBL_PATH = '/data/data_mwbl/'
VSL_PATH = '/data/data_vsl/'

DATA_PATH = ROOT_PATH + MWBL_PATH


def get_grades_years():

    os.chdir(DATA_PATH)

    files_list = []
    for file in os.listdir():
        file_name, file_ext = os.path.splitext(file)
        if file_name == 'README':
            continue  # skip any README files

        grade, year, data_type = tuple(file_name.split('_'))

        if data_type == 'standings' or data_type == 'fixtures':
            continue

        files_list.append((grade, year, data_type))

    files_tuple = tuple(sorted(files_list))

    os.chdir(ROOT_PATH)

    return files_tuple


def initalise_next_round_prediction_yaml():
    with open('_data/next_round_predictions.yaml', 'w') as yamlfile:
        now = datetime.date.today()
        yamlfile.write('metadata:\n')
        yamlfile.write(f'  updated: {now}\n')
        yamlfile.write('grades:\n')


def initalise_current_standings_yaml():
    with open('_data/current_standings.yaml', 'w') as yamlfile:
        now = datetime.date.today()
        yamlfile.write('metadata:\n')
        yamlfile.write(f'  updated: {now}\n')
        yamlfile.write('grades:\n')


@dataclass
class Season:
    year: int
    grade: str
    teams: tuple = field(init=False)
    results: tuple = field(init=False)
    fixtures: tuple = field(init=False)
    longest_name: int = field(init=False)

    def __post_init__(self):
        self.teams = self.initalise_teams()
        self.results = self.initalise_games(self.teams, 'results')
        if self.year == CURRENT_YEAR:
            self.fixtures = self.initalise_games(self.teams, 'fixtures')
        else:
            self.fixtures = None
        self.longest_name = self.initalise_longest_team_name()

    WIN_POINTS = 2
    DRAW_POINTS = 1

    def initalise_teams(self):

        teams = []
        bye = ['bye', 'baseball victoria']

        with open(f'{DATA_PATH}{self.grade}_{self.year}_results.csv') as csvfile:
            results_csv = csv.DictReader(csvfile)

            for game in results_csv:
                team_home = game.get('team_home')
                if team_home.lower() != 'bye' and team_home.lower() != 'baseball victoria':
                    teams.append(Team(team_home, self.grade, int(self.year)))
                team_away = game.get('team_away')
                if team_away.lower() != 'bye' and team_away.lower() != 'baseball victoria':
                    teams.append(Team(team_away, self.grade, int(self.year)))
        teams = set(teams)
        return tuple(teams)

    def initalise_games(self, teams, data_type):

        games = []

        bye = ['bye', 'baseball victoria']

        try:
            with open(f'{DATA_PATH}{self.grade}_{self.year}_{data_type}.csv') as csvfile:
                games_dictreader = csv.DictReader(csvfile)

                for game in games_dictreader:
                    game_dict = dict(game)
                    if game_dict.get('team_home').lower() in bye or game_dict.get('team_away').lower() in bye:
                        continue
                    game_obj = Game.from_dict(teams, game_dict)
                    if game_obj is not None:
                        games.append(game_obj)
                    else:
                        continue
            return tuple(games)
        except FileNotFoundError:
            if self.year == CURRENT_YEAR:
                print(f'Unable to find {data_type} file: {DATA_PATH}{self.grade}_{self.year}_{data_type}.csv')
                pass
            else:
                pass

    def initalise_longest_team_name(self):
        return max(len(team.name) for team in self.teams)

    @property
    def standings(self):

        standings = self.teams
        rank_string = 'win_percentage - wins - losses - draws - runs_scored - runs_allowed'
        rank_order = rank_string.split(' - ')

        for attribute in reversed(rank_order):  # sort from the least important to most important ranking
            standings = sorted(standings, key=lambda team: getattr(team, attribute), reverse=True)

        return tuple(standings)

    @property
    def display_grade(self):
        # works for Seniors but patchy for other clubs
        # for now, used primarily for displaying the prediction output.

        display_grade = self.grade

        display_grade = re.sub(r'([A-Z][a-z]+)', r'\1 ', display_grade)
        display_grade = re.sub(r'([0-9]+)', r'\1 ', display_grade)
        display_grade = re.sub(r' \)', r')', display_grade)
        display_grade = display_grade.strip()

        return display_grade

    def print_season_info(self):
        print(self.grade, self.year)

    def print_standings(self):

        print('-')
        self.print_season_info()
        print('-')
        print('TEAM', ' ' * (self.longest_name - 5), 'W%', 'ELO', 'WINS', 'LOSSES', 'DRAWS', sep='\t')
        for team in self.standings:
            Team.print_team(team, self.longest_name)
        print('-')

    def write_standings_csv(self):
        all_teams = []
        for team in self.standings:
            all_teams.append(team.__dict__)
            fieldnames = team.__dict__.keys()

        with open(f'{DATA_PATH}{self.grade}_{self.year}_standings.csv', 'w') as csvfile:
            standings_writer = csv.DictWriter(csvfile, fieldnames)
            standings_writer.writeheader()
            for team in all_teams:
                standings_writer.writerow(team)

    def predict_next_round(self):

        next_round_number = self.results[-1].round_number + 1

        print(f'{self.display_grade} {self.year} Round {next_round_number} Predictions:')

        if self.fixtures is not None:
            for game in self.fixtures:

                if game.round_number == next_round_number:
                    exp_val_home = calc_exp_value_home(game)
                    home_win_pc = round(exp_val_home * 100)
                    print(f'{game.team_away.name} @ {game.team_home.name}:')
                    print(f'{game.team_home.name.upper()} chance of winning: {round(exp_val_home*100)}%')
                    print(f'{game.team_away.name.upper()} chance of winning: {round((1-exp_val_home)*100)}%')

        else:
            print(f'Unable to predict games - fixture not found')
            pass

        print()

    def append_next_round_prediction_yaml(self):

        next_round_number = self.results[-1].round_number + 1
        indent_spaces = '    '

        if self.fixtures is not None:
            with open('_data/next_round_predictions.yaml', 'a') as yamlfile:
                yamlfile.write(f'  -\n')
                yamlfile.write(f'{indent_spaces}name: \'{self.display_grade} - Round  {next_round_number}\'\n')
                yamlfile.write(f'{indent_spaces}games:\n')

                for game in self.fixtures:
                    if game.round_number == next_round_number:
                        yamlfile.write(f'{indent_spaces}-\n')
                        indent_spaces += '  '
                        exp_val_home = calc_exp_value_home(game)
                        home_win_pc = round(exp_val_home * 100)
                        yamlfile.write(f'{indent_spaces}team_home: \'{game.team_home.name}\'\n')
                        yamlfile.write(f'{indent_spaces}team_away: \'{game.team_away.name}\'\n')
                        yamlfile.write(f'{indent_spaces}chance_home: {home_win_pc}\n')
                        yamlfile.write(f'{indent_spaces}chance_away: {100-home_win_pc}\n')
                    indent_spaces = '    '
        else:
            print(f'Unable to predict games - fixture not found')
            pass

    def append_current_standings_yaml(self):

        next_round_number = self.results[-1].round_number + 1
        indent_spaces = '    '

        with open('_data/current_standings.yaml', 'a') as yamlfile:
            yamlfile.write(f'  -\n')
            yamlfile.write(f'{indent_spaces}name: \'{self.display_grade} - Round  {next_round_number - 1}\'\n')
            yamlfile.write(f'{indent_spaces}teams:\n')
            for team in self.standings:
                yamlfile.write(f'{indent_spaces}-\n')
                indent_spaces += '  '
                yamlfile.write(f'{indent_spaces}team_name: \'{team.name}\'\n')
                yamlfile.write(f'{indent_spaces}elo: \'{round(team.elo)}\'\n')
                yamlfile.write(f'{indent_spaces}win_percentage: \'{round(team.win_percentage, 4)}\'\n')
                yamlfile.write(f'{indent_spaces}runs_scored: \'{team.runs_scored}\'\n')
                yamlfile.write(f'{indent_spaces}runs_allowed: \'{team.runs_allowed}\'\n')
                yamlfile.write(f'{indent_spaces}runs_percentage: \'{round(team.runs_percentage, 4)}\'\n')
                indent_spaces = '    '

    @staticmethod
    def get_team_from_name_string(teams, team_name_string):
        for team in teams:
            if team.name == team_name_string:
                return team


@dataclass
class Game:
    team_home: str
    team_away: str  # should these be the Team object themselves?
    score_home: int = None
    score_away: int = None
    date_time: str = None
    round_number: int = None
    ground: str = None
    is_final: bool = None
    official_status: str = None

    @classmethod
    def from_dict(cls, teams, game_dict):
        '''Take the dictionary returned from reading the csv and turn it into the game object'''
        '''Ideally this will be able to handle some degree of dirtiness or incompletion in the data'''

        team_home = Season.get_team_from_name_string(teams, game_dict['team_home'])
        team_away = Season.get_team_from_name_string(teams, game_dict['team_away'])

        date_time = game_dict['date_time']
        round_number = int(float(game_dict['round_number']))

        # Game.try_key(game_dict, 'ground')
        # ground = game_dict['ground']

        try:
            score_home = int(game_dict['score_home'])
            score_away = int(game_dict['score_away'])
            if team_home is not None and team_away is not None:
                return cls(team_home, team_away, score_home, score_away, date_time, round_number)
        except KeyError:
            if team_home is not None and team_away is not None:
                return cls(team_home, team_away, date_time=date_time, round_number=round_number)
        except ValueError:
            pass

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
        regressed_elo = (float(elo) / regression_factor) + 1500 * ((regression_factor - 1) / regression_factor)
        return regressed_elo

    @staticmethod
    def calc_stat_percent(up, down):
        try:
            return 0.500 + 0.500 * ((up - down) / (up + down))
        except ZeroDivisionError:
            return 0.500

    def print_team(self, longest_name=0):

        print(self.name, ' ' * (longest_name - len(self.name)),
              f'\t{round(self.win_percentage, ndigits=3)}\t{round(self.elo)}\t',
              f'{self.wins}\t{self.losses}\t{self.draws}')


def calc_exp_value_home(game):

    elo_home = game.team_home.elo
    elo_home += hfa
    elo_away = game.team_away.elo

    exp_val_home = 1 / (1 + 10**((elo_away - elo_home) / 400))

    # helpfully, the exp value is also the win probability for the given team.

    return exp_val_home


def calc_elo(game, k=50):

    exp_val_home = calc_exp_value_home(game)
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


def count_diff_values(diff_value):
    diff_value_total += diff_value
    return


def calc_game_mse(game):

    exp_val_home = calc_exp_value_home(game)
    act_val_home = Game.get_actual_value_home(game)
    game_mse = 2 * ((exp_val_home - act_val_home)**2)

    return game_mse


def calc_mean_squared_error(seasons):

    diff_value_total = 0
    n_games = 0

    for season in seasons:
        grade, year, data_type = season
        season = Season(year, grade)
        n_games += len(season.results)
        for game in season.results:
            exp_val_home = calc_exp_value_home(game)
            act_val_home = Game.get_actual_value_home(game)
            diff_value_total += 2 * ((exp_val_home - act_val_home)**2)  # same magnitude for home and away

    return diff_value_total / n_games


def iterate_over_seasons(seasons, filter=False, print_standings=False, predict=False, count_error=False):

    seasons_tse = 0
    n_games = 0

    if predict:
        initalise_next_round_prediction_yaml()
        initalise_current_standings_yaml()

    for season in seasons:
        grade, year, data_type = season
        if filter:
            if filter not in grade:
                continue
        season = Season(year, grade)
        season.display_grade
        for game in season.results:
            Game.record(game)
            calc_elo(game, k)
            if count_error:
                seasons_tse += calc_game_mse(game)
                n_games += len(season.results)

        Season.write_standings_csv(season)

        if print_standings:
            print()
            Season.print_standings(season)

        if predict and year == CURRENT_YEAR:
            Season.predict_next_round(season)
            Season.append_next_round_prediction_yaml(season)
            Season.append_current_standings_yaml(season)

    if count_error and n_games:
        seasons_mse = seasons_tse / n_games
        seasons_mse_formatted = '{:0.4e}'.format(seasons_mse)
        print(f'MSE: {seasons_mse_formatted} at k = {k}, hfa = {hfa}, rf = {regression_factor}')


def guess_who_wins(future_game):

    exp_val_home = calc_exp_value_home(future_game)
    random_threshold = random.random()
    print(random_threshold)
    print(f'{future_game.team_home.name.upper()} CHANCE: {exp_val_home} vs. {future_game.team_away.name.upper()}')
    if random_threshold <= exp_val_home:
        print('The home team has won!')


def guess_rest_of_season(season):
    """
    I want to call the same elo equation with the same parameters EXCEPT using the team.predicted_elo
    """
    pass


seasons = get_grades_years()

hfa = 0
k = 200
regression_factor = 2  # how much of the previous score to get?

iterate_over_seasons(seasons, print_standings=True, predict=True)
