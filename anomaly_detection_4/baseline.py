import pandas as pd

LOGIN_PATH = "baseline_logins.csv"


def load_daily_failures(path):
    """Load one row per day of historical login failures."""
    daily = pd.read_csv(path)
    return daily


def average_failures(daily):
    """Calculate the average daily failed-login count."""
    counts = daily["failed_logins"]
    average = counts.mean()
    return average


def maximum_failures(daily):
    """Return the largest daily failed-login count."""
    counts = daily["failed_logins"]
    maximum = counts.max()
    return maximum


def make_limit(maximum):
    """Set the alert threshold one above the historical maximum."""
    limit = maximum + 1
    return limit
