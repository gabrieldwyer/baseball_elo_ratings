# Melbourne Winter Baseball League (MWBL) Elo Ratings Project

## Overview

This is a project to develop a reasonably sophisticated prediction model based on the elo rating system.

It is intended as a learning exercise.

Any advice on how to improve the model, or the code, is more than welcome.

Currently, the data used to generate this model is not provided here. I want to ensure I have permission to upload it prior to releasing it on github.

Some notes on nomenclature:
As the elo system is being applied here to a game that has scores, it is important to be precise and careful when it comes to word usage:
- the elo value is known as a rating
- the value is W/L/D (1/0/0.5) respectively. This is often known as the expected score in elo methods, but I think it makes more sense to call it a value
- the score is the 'baseball score' in the traditional sense i.e. 12 v. 5

## Future improvements

- make base data available
- include some kind of user input
- include further predictions for the league other than the next round:
    - Monte Carlo method
    - mathematical calculation method
- learn to discount Bye games
- learn to distinguish between finals and regular season
- graphs, and pretty visualisations
- interactivity within the graphs
- broader design goals including more sophisticated implementations of my personal website and portfolio
- determine the adequate home field advantage
- include a margin of victory metric to improve the fidelity of the model and take full advantage of the data available to me
- create, test, and upload multiple possible models to compare which is best and why:
    - Home always wins
    - Offensive and Defensive Elo ratings?
- What's the difference in skill between the grades?
    - Use relegation elo etc. to determine?
    - This would require multiple seasons of data. (maybe)
- How would elo corrections work? Linear conversion?
- For one season of data - lowest elo Grade A = highest elo Grade B?
- How similar are teams from one game to the next?
- apply this model and more to other situations i.e. The Big Bash

I also believe that the data I currently possess may be enough to determine a Park Factor for each of the parks used by the league.

This README could be improved by adding plain language explanations to a number of its elements, to ensure the lay-person can understand, in at least broad strokes, what is going on, and how accurate/inaccurate the model/data/prediction is. Assumptions should also be listed and described.

## Learn more

Read more about the elo rating system:
- link to wikipedia article on elo ratings
- link to fivethirtyeight's elo Ratings
- link to AFL elo ratings including that PhD?
- link to the NFL margin of error elo ratings?
