import math
from statistics import pstdev

# Given execution results (from your JSON)
aggregator_map = {
    "commitsMariona_FT": 6,
    "commitszThePlatano": 1,
    "commitsMChecaH": 0,
    # "commitseducole": 8,
    # "commitsMiguelM1D": 5,
    # "commitsAr1e1": 0,
    # "commitsvictorlopezlanuza01": 6,
    # "commitsmarcperezg": 24
}
commitsTotal = 7

# List of team member keys in the same order as in your formula
team_members = [
    "commitszThePlatano",
    "commitsMChecaH",
    "commitsMariona_FT",
    # "commitsMariona_FT",
    # "commitsvictorlopezlanuza01",
    # "commitsMChecaH",
    # "commitsmarcperezg",
    # "commitsAr1e1"
]

# 1. Compute the normalized fractions for each team member
fractions = [
    aggregator_map.get(member, 0) / commitsTotal for member in team_members
]

# 2. Compute the population standard deviation on these fractions
# Note: The fractions should sum to 1, so the mean should be 1/8 = 0.125.
metric_value = pstdev(fractions)  # pstdev uses population (ddof=0) by default

print(f"Normalized fractions: {fractions}")
print(f"Calculated metric (population stdev): {metric_value:.8f}")
