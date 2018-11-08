import csv
import random

team_name_list = [
    'Sluggers', 'Eagles', 'Bearcats', 'Travelers', 'Tigers', 'Defenders', 'Whitecaps', 'Blue Birds', 'Flyers',
    'Raptors', 'Americans', 'Bandits', 'The Wild', 'Saints', 'Falcons', 'Sounders', 'Thunder', 'Marlins', 'Flash',
    'Nuggets', 'Homers', 'Rampage', 'Hitters', 'Chargers', 'Indians', 'Rage', 'LakeHawks', 'Crush', 'Padres',
    'Zephyrs', 'Tsunamis', 'Reds', 'Lightning', 'Oilers', 'Podunk Posse', 'Devils', 'Seabirds', 'Coyotes', 'Cowboys',
    'Raiders', 'Lightning', 'Bears', 'Avalanche', 'Orediggers', 'Surf', 'Pistons', 'Crew', 'Union']


def create_team_name(name_list):
    name_index = random.randint(0, len(team_name_list) - 1)
    name = name_list[name_index]
    return name


def create_score():
    score = int(random.triangular(0, 10))
    return score


def generate_game():
    team_home = create_team_name(team_name_list)
    team_away = create_team_name(team_name_list)
    score_home = create_score()
    score_away = create_score()
    date_time = '2018-09-30 12:00:00'
    return [date_time, team_home, score_home, team_away, score_away]


game_list = []
num_games = 12

for n in range(num_games):
    game_list.append(generate_game())

with open('_data/test_data.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    writer.writerow(['date_time', 'team_home', 'score_home', 'team_away', 'score_away'])

    for game in game_list:
        print(game)
        writer.writerow(game)
