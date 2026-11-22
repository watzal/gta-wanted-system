import numpy as np


# per-step (5-second) probabilities for each star level

STARS    = [1, 2, 3, 4, 5]
HIDE     = [0.30, 0.25, 0.20, 0.15, 0.10]  # spotted -> hiding
ESCALATE = [0.10, 0.10, 0.08, 0.06, 0.00]  # spotted -> one more star
BUSTED   = [0.06, 0.05, 0.03, 0.01, 0.00]  # spotted -> arrested
WASTED   = [0.01, 0.02, 0.04, 0.07, 0.10]  # spotted -> killed
ESCAPE   = [0.25, 0.18, 0.12, 0.08, 0.05]  # hiding -> search called off
RESPOT   = [0.15, 0.20, 0.25, 0.30, 0.35]  # hiding -> found again

SECONDS_PER_STEP = 5
ENDINGS = ["Escaped", "Busted", "Wasted"]

# building the transition matrix for the Markov chain

def build(hide=HIDE, respot=RESPOT):
    states = ([f"{k}★ Spotted" for k in STARS] +
              [f"{k}★ Hiding" for k in STARS] +
              ENDINGS)
    P = np.zeros((13, 13))       # 13 states: 5 Spotted, 5 Hiding, 3 endings
    S = lambda k: k - 1          # index of (k, Spotted)
    H = lambda k: 5 + k - 1      # index of (k, Hiding)
    ESC, BUS, WAS = 10, 11, 12   # indices of the three absorbing states

    for k in STARS:
        i = k - 1
        # Spotted
        P[S(k), H(k)] = hide[i]
        if k < 5:
            P[S(k), S(k + 1)] = ESCALATE[i]
        P[S(k), BUS] = BUSTED[i]
        P[S(k), WAS] = WASTED[i]
        P[S(k), S(k)] = 1 - P[S(k)].sum()   # nothing changes
        # Hiding
        P[H(k), ESC] = ESCAPE[i]
        P[H(k), S(k)] = respot[i]
        P[H(k), H(k)] = 1 - P[H(k)].sum()

    for a in (ESC, BUS, WAS):
        P[a, a] = 1                          # absorbing states

    assert np.allclose(P.sum(axis=1), 1)    # every row sums to 1
    assert (P >= 0).all()                    # no negative probabilities
    return states, P



# Solving by counting: follow 1,000 players until every chase ends

def follow_players(P, start, n_players=1000, max_steps=200):
    players = np.zeros(13)
    players[start] = n_players
    steps_in_chase = 0.0
    for _ in range(max_steps):
        steps_in_chase += players[:10].sum()   # players still chasing spend one more step
        players = players @ P                  # every group splits up by its rules
    return players[10:], steps_in_chase / n_players



# Double-check with a Monte Carlo simulation

def simulate(P, start, runs=100000, seed=42):
    rng = np.random.default_rng(seed)
    endings, lengths = np.zeros(3), []
    for _ in range(runs):
        s, steps = start, 0
        while s < 10:                      # still in a chase state
            s = rng.choice(13, p=P[s])     # choosing the next state
            steps += 1
        endings[s - 10] += 1
        lengths.append(steps)
    return endings / runs, np.array(lengths)



if __name__ == "__main__":
    states, P = build()

    # condition in the blog: 1,000 players starting at 3★ Spotted
    print("Following 1,000 players who start at 3★ Spotted")
    print(f"{'Time':>8} {'Spotted':>8} {'Hiding':>8} {'Escaped':>8} {'Busted':>8} {'Wasted':>8}")
    players = np.zeros(13)
    players[2] = 1000  # 1000 players start at 3★ Spotted
    for step in range(201):  # 200 steps of 5 seconds, about 17 minutes
        if step in (0, 1, 2, 6, 12, 24, 200):
            print(f"{step * SECONDS_PER_STEP:>7}s "
                  f"{players[:5].sum():8.0f} {players[5:10].sum():8.0f} "
                  f"{players[10]:8.0f} {players[11]:8.0f} {players[12]:8.0f}")
        players = players @ P  # every group splits up by its rules

    # results from every star level: counting vs. simulation
    print("\nStart        Escape(count) Escape(sim)  Busted  Wasted  Avg chase  Median  90th pct")
    results = []
    for k in STARS:
        start = k - 1
        counts, avg_steps = follow_players(P, start)
        share = counts / counts.sum()
        sim, lengths = simulate(P, start)
        results.append(share)
        print(f"{states[start]:<12} {share[0]*100:12.1f}% {sim[0]*100:10.1f}% "
              f"{share[1]*100:6.1f}% {share[2]*100:6.1f}% "
              f"{avg_steps * SECONDS_PER_STEP:8.0f}s "
              f"{np.median(lengths) * SECONDS_PER_STEP:6.0f}s "
              f"{np.percentile(lengths, 90) * SECONDS_PER_STEP:8.0f}s")
