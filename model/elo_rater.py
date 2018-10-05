# elo_rater.py

# IMPROVEMENTS to be made:
# - determine the difference between the regular season and finals
# - write the updated elo to the results DataFrame and save it so a csvfile
# - write a csv file with elo over time for each team?
# - find the bye rounds and ignore them
# - scrape weather from the closest weather station to
# - treat byes as NOT A TEAM

import os

import matplotlib.pyplot as plt
import pandas as pd

# initalising functions

os.chdir('/Users/gabrieldwyer/Documents/04_Programming/baseball_elo_ratings/')


def get_grade_year(path):
    """Generate the grade and year based on the file names in the data directory."""

    root_path = os.getcwd()
    os.chdir(root_path + "/" + path)
    print(os.getcwd())
    file_list = []
    for file in os.listdir():
        file_name, file_ext = os.path.splitext(file)
        if file_name == 'README':
            continue  # skip any README.md files
        grade, year, file_type = tuple(file_name.split('_'))
        file_list.append((grade, year, file_type))

    return sorted(file_list)


def get_games(csvfile):
    """Return the results DataFrame for the results csv in the current working directory."""

    df = pd.read_csv(os.getcwd() + '/' + csvfile)
    return df


def get_teams(csvfile, grade, year):
    """Return a dictionary of Team objects with team.name string keys."""

    teams = {}
    df = pd.read_csv(os.getcwd() + '/' + csvfile)
    all_teams_df = pd.concat([df.team_home, df.team_away])
    for team in all_teams_df.unique():
        teams[team] = Team(team, grade, year)
    return teams


def input_grade(grade_input=False):
    """Ask the user what grade they would like to analyse. Needs updating."""

    if grade_input is False:
        grade_input = input('Which grade do you want? ')
    grade_dict = {'B Grade': 'B', 'B Reserves': 'BRes'}
    grade = grade_dict[grade_input]
    return grade

# define classes


class League:

    def __init__(self, year, grade):
        self.year = year
        self.grade = grade
        self.teams = get_teams(self.results, self.grade, self.year)

    @property
    def results(self):
        # maybe this should actually be the DataFrame?
        try:
            return '%s_%s_results.csv' % (self.grade, self.year)
        except FileNotFoundError:
            return None

    def print_league_info(self):
        """Print the league information."""

        print(self.grade, self.year)

    def print_standings(self):
        """Find the currrent standings and print them in order of points. Break ties with R%."""

        print('-')
        League.print_league_info(self)
        print('-')
        print('TEAM', '\t\t', 'POINTS', 'R%', 'ELO', 'WINS', 'LOSSES', 'DRAWS', sep='\t')
        team_points = {}
        for team in self.teams.values():
            team_points[team] = [team.points + 0.1 * team.runs_percentage]
        # Run percantage is the second sorting criteria of the standings
        # 0 =< R% =< 1, and higher R% is better
        # thus it can simply be added to the points integer to create a composite sorting value
        # R% is multiplied by 0.1 to avoid attributing a perfect record (i.e. no runs allowed) from counting as a point

        while len(team_points) > 0:
            key_max = max(team_points.keys(), key=(lambda k: team_points[k]))
            Team.print_most(key_max)
            team_points.pop(key_max)
        print('-')

    def print_elo(self):
        """Print elo ratings of each team."""

        for team in self.teams:
            Team.print_elo(self.teams[team])

    def write_standings_csv(self):
        """Convert the teams dictionary to a DataFrame and save it as a csv file."""

        all_teams = []
        for team in self.teams:
            all_teams.append(self.teams[team].__dict__)
        standings_df = pd.DataFrame(all_teams)
        standings_df.set_index('name', inplace=True)
        standings_df.to_csv('%s_%s_standings.csv' % (self.grade, self.year))


class Club:

    def __init__(self, colours, alias):
        self.colours = colours
        self.alias = alias


def get_elo(self):
    """Get the initial elo rating, based on the team elo of the prior season."""

    print(self.name, 'returning: ', self.returning)
    if not self.returning:
        return 1500
    else:
        previous_standings = pd.read_csv('%s_%s_standings.csv' % (grade, year - 1), index_col=0)
        previous_elo = previous_standings.elo.loc[self.name]
        return previous_elo / 2 + 750  # regress elo halfway to the mean


class Team(Club):

    def __init__(self, name, grade, year, colours='NaN', alias='NaN', homeground='NaN',
                 played=0, won=0, lost=0, drew=0, points=0, runs_scored=0, runs_allowed=0):
        self.name = name
        self.grade = grade
        self.year = year
        Club.__init__(self, colours='NaN', alias='NaN')
        self.homeground = homeground
        self.played = played
        self.won = won
        self.lost = lost
        self.drew = drew
        self.runs_scored = runs_scored
        self.runs_allowed = runs_allowed
        self.elo = get_elo(self)

    def __repr__(self):
        return self.name

    @property
    def runs_percentage(self):
        """Calculate the run percentage."""

        try:
            return 0.500 + 0.500 * ((self.runs_scored - self.runs_allowed) / (self.runs_scored + self.runs_allowed))
        except ZeroDivisionError:
            return 0.500

    @property
    def win_percentage(self):
        """Calculate the win percentage."""

        try:
            return 0.500 + 0.500 * ((self.won - self.lost) / (self.won + self.lost))
        except ZeroDivisionError:
            return 0.500

    @property
    def points(self):
        """Calculate the points attribute dynamically from won and drew."""

        return self.won * 2 + self.drew

    @property
    def returning(self):
        """Check to see if the Team object played in the same grade in the previous year."""

        try:
            previous_standings = pd.read_csv('%s_%s_standings.csv' % (grade, year - 1), index_col=0)
        except FileNotFoundError:
            return False

        try:
            return str(self.name) in previous_standings.index.values
        except IndexError:
            return False

    def print_elo(self):
        """Print the formatted elo rating of the team."""

        print(self.name.upper(), ' ' * (20 - len(self.name)), self.elo)

    def print_most(self):
        """Print the formatted main attributes of the team."""

        print(self.name.upper(), ' ' * (23 - len(self.name)), self.points,
              "%.3f" % round(self.runs_percentage, ndigits=3), "%4g" % round(self.elo),
              self.won, self.lost, self.drew, sep='\t')

    def print_all(self):
        """Print the formatted attributes of the team."""

        print(self.name.upper(), ' ' * (20 - len(self.name)), self.points, self.runs_percentage, self.elo, self.played,
              self.won, self.lost, self.drew, self.runs_scored, self.runs_allowed)


# calculation and writing functions


def get_team_score(game):
    """Set local variables for teams and scores for further calculation functions."""

    team_home, team_away = (league.teams[game.get('team_home')], league.teams[game.get('team_away')])
    score_home, score_away = (int(game.get('score_home')), int(game.get('score_away')))
    return team_home, team_away, score_home, score_away


def run_recorder(team_home, team_away, score_home, score_away):
    """Add the runs scored to both Team objects."""

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


def record_win_loss_draw(winner, loser, draw=False):
    """"""

    if draw is False:
        winner.won += 1
        loser.lost += 1
    elif draw is True:
        winner.draw += 1
        loser.draw += 1


def check_elo_upset(winner, loser, upsets):
    """Add one to the upset variable if the loss what an upset."""

    if winner.elo > loser.elo:
        upsets += 1
        return upsets


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
    # add a writing part in here to write the results_parsed/plus file with elos


def add_home_field_advantage(team_home, home_field_advantage=0):
    """Add the home field advantage to the home team's elo and return the modified rating."""

    # is this the best way to apply a home_field_advantage
    home_elo_plus = team_home.elo + home_field_advantage
    return elo_home_plus


def predict_next_round(grade, df):
    """Predict the next round."""

    length = len(df)
    fixture = pd.read_csv('%s_2018_fixture.csv' % grade, index_col=0)
    fixture.dropna(axis='columns', how='all', inplace=True)
    fixture.columns = ['date_time', 'team_home', 'team_away', 'ground']
    next_round = fixture.loc[length - 1:length + 2, ['team_home', 'team_away', 'ground']]
    print(grade, 'predictions:')
    for game in range(len(next_round)):
        home_chance = expected_value(next_round.iloc[game])
        print(next_round.iloc[game, 0] + " vs. " + next_round.iloc[game, 1])
        print(next_round.iloc[game, 0] + '\'s chance of winning: ' + str(round(home_chance * 100)) + '%')
        print(next_round.iloc[game, 1] + '\'s chance of winning: ' + str(round((1 - home_chance) * 100)) + '%')
        print('------')


# This is the calling bit!

seasons = get_grade_year('data/data_working')
print(seasons)

for season in seasons:
    grade, year, file_type = season
    year = int(year)
    print('-')
    print(season)
    if file_type == 'standings' or file_type == 'fixture':
        continue
    league = League(year, grade)
    League.print_elo(league)
    results_df = pd.read_csv(league.results, index_col=0, header=0)
    for row in range(len(results_df)):
        calculate_elo(results_df.loc[row])
    if year == 2018:
        predict_next_round(grade, results_df)

    League.print_standings(league)
    League.write_standings_csv(league)


"""
loop over for k in range(1, 50) to fine-tune which k value is IDEAL.

This k loop needs to run over the entire dataset. - also for each league? Which leagues does the model work best for?

upsets should be a list - k = 1, upsets[k-1]

minimum value on the list?

loop over home field advantage? 2 axes ^> with colour representing the number of upsets
"""

#
# for k in range(1, 50):
#     upsets = 0
#     calculate_elo()
#     upsets = check_upset(winner, loser, upsets)
