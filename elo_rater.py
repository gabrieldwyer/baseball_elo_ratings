# import matplotlib.pyplot as plt
import pandas as pd
import os


def get_games(csvfile):
    df = pd.read_csv(csvfile)
    return df


def get_teams(csvfile):
    teams = {}
    df = pd.read_csv(csvfile)
    for team in df.team_home.unique():
        teams[team] = Team(team)
    return teams


class League():

    def __init__(self, year, grade):
        self.year = year
        self.grade = grade
        self.teams = get_teams(self.results)

    @property
    def results(self):
        return '_data_working/%s_%s_results.csv' % (self.grade, self.year)

    @property
    def first_season(self):
        return not os.path.isfile('%s_%s_standings.csv' % (self.grade, (self.year)-1))

    def print_league_info(self):
        print(self.grade, self.year)

    def print_unordered_standings(self):
        """Print team values."""

        print('-')
        print('TEAM \t\t POINTS R% ELO WINS LOSSES DRAWS')
        print('-')
        for team in self.teams:
            Team.print_most(self.teams[team])

    def print_ordered_standings(self):
        """Find the currrent standings and print them in order of points. Break ties with R%."""

        print('-')
        League.print_league_info(self)
        print('-')
        print('TEAM', '\t\t', 'POINTS', 'R%', 'ELO', 'WINS', 'LOSSES', 'DRAWS', sep='\t')
        team_points = {}
        for team in self.teams.values():
            team_points[team] = [team.points + 0.1*team.runs_percentage]
        while len(team_points) > 0:
            key_max = max(team_points.keys(), key=(lambda k: team_points[k]))
            Team.print_most(key_max)
            team_points.pop(key_max)
        print('-')

    # def write_standings_csv(self):
    #     all_teams = []
    #     for team in self.teams:
    #         all_teams.append(self.teams[team].__dict__)
    #     standings_df = pd.DataFrame(all_teams)
    #     standings_df.set_index('name', inplace=True)
    #     standings_df.to_csv('%s_%s_standings.csv' % (self.grade, self.year))


class Team():

    def __init__(self, name, colours='NaN', alias='NaN', homeground='NaN', elo=1500,
                 played=0, won=0, lost=0, drew=0, points=0, runs_scored=0, runs_allowed=0, returning='NaN'):
        self.name = name
        self.colours = colours
        self.alias = alias
        self.homeground = homeground
        self.elo = elo
        self.played = played
        self.won = won
        self.lost = lost
        self.drew = drew
        self.runs_scored = runs_scored
        self.runs_allowed = runs_allowed
        self.returning = returning

    @property
    def runs_percentage(self):
        if self.runs_scored == 0:
            return 500
        else:
            return 0.500 + 0.500*((self.runs_scored-self.runs_allowed)/(self.runs_scored+self.runs_allowed))

    @property
    def win_percentage(self):
        if self.won == 0:
            return 0.500
        else:
            return 0.500 + 0.500*((self.won-self.lost)/(self.won+self.lost))

    @property
    def points(self):
        return self.won * 2 + self.drew

    def __repr__(self):
        return self.name

    def print_elo(self):
        print(self.name.upper())
        print(self.elo)

    def print_most(self):
        print(self.name.upper(), ' '*(23-len(self.name)), self.points,
              "%.3f" % round(self.runs_percentage, ndigits=3), round(self.elo),
              self.won, self.lost, self.drew, sep='\t')

    def print_all(self):
        print(self.name.upper(), ' '*(20-len(self.name)), self.points, self.runs_percentage, self.elo, self.played,
              self.won, self.lost, self.drew, self.runs_scored, self.runs_allowed)


def get_grade(grade_input=False):
    """Ask the user what grade they would like to analyse"""

    if grade_input is False:
        grade_input = input('Which grade do you want? ')
    grade_dict = {'B Grade': 'B', 'B Reserves': 'BRes'}
    grade = grade_dict[grade_input]
    return grade

# calculation functions


def get_team_score(game):
    team_home, team_away = (league.teams[game.get('team_home')], league.teams[game.get('team_away')])
    score_home, score_away = (int(game.get('score_home')), int(game.get('score_away')))
    return team_home, team_away, score_home, score_away


def run_recorder(team_home, team_away, score_home, score_away):
    """Add the runs scored to both teams."""

    team_home.runs_scored += score_home
    team_home.runs_allowed += score_away
    team_away.runs_scored += score_away
    team_away.runs_allowed += score_home


def win_lose_or_draw(game):
    """Compare the score of each team to determine the outcome(W/L/D) for each team."""

    team_home, team_away, score_home, score_away = get_team_score(game)
    run_recorder(team_home, team_away, score_home, score_away)

    team_home.played += 1
    team_away.played += 1

    act_v_home = 0  # placeholder
    if score_home > score_away:
        team_home.won += 1
        team_away.lost += 1
        return act_v_home + 1

    elif score_home < score_away:
        team_home.lost += 1
        team_away.won += 1
        return act_v_home

    elif score_home == score_away:
        team_home.drew += 1
        team_away.drew += 1
        return act_v_home + 0.5


def expected_value(game):
    """Calculate the expected value of a match for each team, based on their respective elos."""

    # retrieves the relevant elo scores
    elo_home = league.teams[game.get('team_home')].elo
    elo_away = league.teams[game.get('team_away')].elo

    exp_v_home = 1 / (1 + 10**((elo_away - elo_home) / 400))
    # helpfully, the expected score is actually the same as the win probability
    return exp_v_home


def calculate_elo(game, k=40):
    """Calculate the updated elo rating of each team following a game."""

    # calculation of expected score for each team
    exp_v_home = expected_value(game)
    act_v_home = win_lose_or_draw(game)

    # home_val + away_val = 1, therefore we can do this:
    exp_v_away = 1 - exp_v_home
    act_v_away = 1 - act_v_home

    # calculates and writes the new elo rank
    elo_home_new = league.teams[game.get('team_home')].elo + k * (act_v_home - exp_v_home)
    elo_away_new = league.teams[game.get('team_away')].elo + k * (act_v_away - exp_v_away)

    league.teams[game.get('team_home')].elo = elo_home_new
    league.teams[game.get('team_away')].elo = elo_away_new


# This is the calling bit!

league = League(2018, 'BGrade')

results_df = pd.read_csv(league.results, index_col=0, header=0)

for row in range(len(results_df)):
    calculate_elo(results_df.loc[row])

League.print_ordered_standings(league)
