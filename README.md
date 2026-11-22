# Modelling GTA's Wanted System before GTA VII

## The model

A GTA-style police chase modeled as an **absorbing Markov chain**:

- **13 states:** 5 star levels × (Spotted, Hiding), plus 3 endings (Escaped, Busted, Wasted)
- **1 step = 5 seconds** of chase
- Each step, a player moves between states using fixed probabilities

This is a deliberately **naive model**. The probabilities are designed by hand to follow the general logic of GTA V's wanted system (higher stars make escaping harder and surviving less likely). They are not measured from the game, and this is not Rockstar's actual police AI.

## How to run

```bash
pip install -r requirements.txt
python wanted_system.py
```

The Monte Carlo check plays 500,000 simulated chases, so the script takes around 30 seconds.

## What the code does

1. **`build()`** turns the per-step probabilities into a 13×13 transition matrix and checks that every row sums to 1.
2. **`follow_players()`** follows 1,000 players step by step until every chase ends. This gives the chance of each ending and the average chase length.
3. **`simulate()`** double-checks the results with a Monte Carlo simulation, playing out 100,000 random chases from each star level, and measures how spread out chase lengths are.

## Ideas to make it better

- Estimate the probabilities from real gameplay instead of designing them
- Add more variables to the state (vehicle, police units, location, time of day)
- Split hiding into stages to model the search timer
- Try a continuous-time Markov chain