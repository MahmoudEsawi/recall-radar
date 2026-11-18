import numpy as np
import pandas as pd
from scipy.stats import poisson

INPUT_CSV = "group_monthly_counts.csv"
OUTPUT_CSV = "trend_poisson_features.csv"
WINDOW = 12
MIN_RATE = 0.5
P_THRESHOLD = 0.001
SEP = "||"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 60)

long = pd.read_csv(INPUT_CSV, parse_dates=["month"])
long["group"] = long["MAKETXT"] + SEP + long["MODELTXT"] + SEP + long["SYSTEM"]

W = long.pivot(index="month", columns="group", values="complaints").sort_index()
print("Groups:", W.shape[1], "| Months:", W.shape[0])
print("From", W.index.min().date(), "to", W.index.max().date())

c = np.arange(WINDOW) - (WINDOW - 1) / 2
sxx = (c ** 2).sum()
slope = sum(c[k] * W.shift(WINDOW - 1 - k) for k in range(WINDOW)) / sxx
mean_in_window = W.rolling(WINDOW).mean()
rel_slope = slope / mean_in_window.clip(lower=1)

expected = W.shift(1).rolling(WINDOW).mean().clip(lower=MIN_RATE)
actual = W.astype(float)
p_value = pd.DataFrame(
    poisson.sf(actual.values - 1, expected.values),
    index=W.index,
    columns=W.columns,
)
ratio = actual / expected

def to_long(frame, name):
    out = frame.reset_index().melt(id_vars="month", var_name="group", value_name=name)
    return out

table = to_long(actual, "complaints")
for frame, name in [
    (expected, "expected"),
    (ratio, "spike_ratio"),
    (p_value, "poisson_p"),
    (slope, "slope12"),
    (rel_slope, "rel_slope12"),
]:
    table[name] = to_long(frame, name)[name].values

table = table.dropna(subset=["expected", "slope12"]).copy()
table["spike_flag"] = ((table["poisson_p"] < P_THRESHOLD) & (table["complaints"] >= 5)).astype(int)

parts = table["group"].str.split(SEP, regex=False, expand=True)
table["MAKETXT"], table["MODELTXT"], table["SYSTEM"] = parts[0], parts[1], parts[2]
table = table.drop(columns="group")
first = ["MAKETXT", "MODELTXT", "SYSTEM", "month"]
table = table[first + [c for c in table.columns if c not in first]]
table.to_csv(OUTPUT_CSV, index=False)
print("Saved", OUTPUT_CSV, "with", len(table), "rows")

print("\nShare of group-months flagged as spikes:", f"{table['spike_flag'].mean():.2%}")

latest = table["month"].max()
now = table[table["month"] == latest].copy()
print("\nLatest month:", latest.date(), "| spikes flagged:", int(now["spike_flag"].sum()))

cols = ["MAKETXT", "MODELTXT", "SYSTEM", "complaints", "expected", "spike_ratio", "poisson_p"]
spikes = now[now["spike_flag"] == 1].sort_values("spike_ratio", ascending=False).head(15)
print("\nTop spikes in the latest month:")
print(spikes[cols].round(4).to_string(index=False))

rising = now[now["expected"] >= 5].sort_values("rel_slope12", ascending=False).head(15)
print("\nFastest rising groups (last 12 months, relative slope per month):")
print(rising[["MAKETXT", "MODELTXT", "SYSTEM", "complaints", "slope12", "rel_slope12"]].round(3).to_string(index=False))
