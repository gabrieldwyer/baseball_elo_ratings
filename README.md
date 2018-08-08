---
layout: page
title: About
permalink: /about/
---

# Melbourne Winter Baseball League (MWBL) Elo Ratings Project

## Overview

This is a project to develop a reasonably sophisticated prediction model based on the Elo rating system.

It is intended as a learning exercise.

Any advice on how to improve the model, or the code, is more than welcome.

Currently, the data used to generate this model is not provided here. I want to ensure I have permission to upload it prior to releasing it on github.

Some notes on nomenclature:
As the Elo system is being applied here to a game that has scores, it is important to be precise and careful when it comes to word usage:
- the Elo value is known as a rating
- the value is W/L/D (1/0/0.5) respectively. This is often known as the expected score in Elo methods, but I think it makes more sense to call it a value
- the score is the 'baseball score' in the traditional sense i.e. 12 v. 5

## Navigating the directories

On (github)[github], all of the directories with the underscore prefix are for jekyll. All other directories are directly related to the project itself. I imagine in time, this distinction will grow increasingly vague as better web visualisations are achieved.

## Future improvements

- make base data available
- include some kind of user input
- include further predictions for the league other than the next round:
    - Monte Carlo method
    - mathematical calculation method
- learn to discount Bye games
- learn to distinguish between finals and regular season
- graphs, and pretty visualisations - D3.js? SVG? Not sure...
- interactivity within the graphs
- broader design goals including more sophisticated implementations of my personal website and portfolio
- determine the adequate home field advantage
- include a margin of victory metric to improve the fidelity of the model and take full advantage of the data available to me
- create, test, and upload multiple possible models to compare which is best and why:
    - Home always wins
    - Offensive and Defensive Elo ratings?
- What's the difference in skill between the grades?
    - Use relegation Elo etc. to determine?
    - This would require multiple seasons of data. (maybe)
- How would Elo corrections work? Linear conversion?
- For one season of data - lowest Elo Grade A = highest Elo Grade B?
- How similar are teams from one game to the next?
- apply this model and more to other situations i.e. The Big Bash

I also believe that the data I currently possess may be enough to determine a Park Factor for each of the parks used by the league.

This README could be improved by adding plain language explanations to a number of its elements, to ensure the lay-person can understand, in at least broad strokes, what is going on, and how accurate/inaccurate the model/data/prediction is. Assumptions should also be listed and described.

## Assumptions

Computers operate in binary, whereas humans typically work in decimal. At first glance, this distinction should be largely superficial -  however, it works out that (decimal numbers a represented as binary fractions on computers)[https://docs.python.org/3/tutorial/floatingpoint.html#tut-fp-issues]. In the same way that 0.3 (3/10) is not precisely 1/3, and neither is 0.33 (3/10 + 3/100), many of these binary fractions approximate the actual value to 53 bits. Ultimately, this problem has a minor to zero effect on the model, but I found it interesting nonetheless. There is the `fraction` module that allows for exact arithmetic fractions, but it's probably overkill to use it here.

## Learn more

Read more about Elo rating systems and predictive models in general:
- (Elo rating system - Wikipedia)[https://en.wikipedia.org/wiki/Elo_rating_system]
- fivethirtyeight's (MLB)[https://fivethirtyeight.com/features/how-our-mlb-predictions-work/], (NBA)[https://projects.fivethirtyeight.com/complete-history-of-the-nba/], and (NFL)[https://projects.fivethirtyeight.com/complete-history-of-the-nfl/] Elo ratings
- (The Arc AFL Footy Elo ratings)[https://thearcfooty.com/2016/12/29/introducing-the-arcs-ratings-system/]
- (Predicting Outcomes in Australian Rules Football PhD)[https://researchbank.rmit.edu.au/eserv/rmit:160744/Ryall.pdf]
