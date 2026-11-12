"""
Time-Series & Trend Analysis (Linear Regression Slopes & Poisson Spike Baselines).
Maintained by Aya.
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm


def compute_monthly_trend_slope(counts: list):
    """
    Computes linear regression slope and p-value for complaint growth over time.
    """
    if len(counts) < 2:
        return 0.0, 1.0
    x = np.arange(len(counts))
    y = np.array(counts)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, p_value


def fit_poisson_baseline(historical_counts: list):
    """
    Fits a Poisson GLM to estimate the expected baseline count and identify surges.
    """
    if len(historical_counts) < 3:
        return np.mean(historical_counts) if historical_counts else 0.0
    
    y = np.array(historical_counts)
    X = sm.add_constant(np.arange(len(y)))
    try:
        model = sm.GLM(y, X, family=sm.families.Poisson()).fit()
        expected_next = model.predict(np.array([[1, len(y)]]))[0]
        return expected_next
    except Exception:
        return float(np.mean(y))
