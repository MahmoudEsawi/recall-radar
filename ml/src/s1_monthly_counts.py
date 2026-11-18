import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

ZIP_PATH = "FLAT_CMPL.zip"

COLUMNS = {
    0: "CMPLID",
    3: "MAKETXT",
    4: "MODELTXT",
    5: "YEARTXT",
    6: "CRASH",
    7: "FAILDATE",
    8: "FIRE",
    9: "INJURED",
    10: "DEATHS",
    11: "COMPDESC",
    15: "DATEA",
}

df = pd.read_csv(
    ZIP_PATH,
    sep="\t",
    header=None,
    usecols=list(COLUMNS.keys()),
    encoding="latin-1",
    quoting=3,
    on_bad_lines="skip",
    dtype=str,
)
df = df.rename(columns=COLUMNS)

print("Rows loaded:", len(df))
print(df.head())

df["FAILDATE"] = pd.to_datetime(df["FAILDATE"], format="%Y%m%d", errors="coerce")
df["DATEA"] = pd.to_datetime(df["DATEA"], format="%Y%m%d", errors="coerce")

last_added = df["DATEA"].max()
print("DATEA range:", df["DATEA"].min().date(), "to", last_added.date())
print("Missing FAILDATE:", df["FAILDATE"].isna().sum())

bad = (df["FAILDATE"] < "1990-01-01") | (df["FAILDATE"] > last_added)
print("Invalid FAILDATE (too old or in the future):", bad.sum())
print(df.loc[bad, "FAILDATE"].dt.year.value_counts().sort_index())
df.loc[bad, "FAILDATE"] = pd.NaT

by_fail = df.dropna(subset=["FAILDATE"]).set_index("FAILDATE").resample("MS").size()
by_added = df.dropna(subset=["DATEA"]).set_index("DATEA").resample("MS").size()

monthly = pd.DataFrame({"by_failure_date": by_fail, "by_date_added": by_added})
monthly.index.name = "month"
monthly.to_csv("monthly_counts.csv")
print(monthly.tail(12))

ax = monthly.plot(figsize=(11, 4), title="NHTSA complaints per month")
ax.set_ylabel("Number of complaints")
plt.tight_layout()
plt.savefig("monthly_counts.png", dpi=150)

print(df["MAKETXT"].value_counts().head(10))
print(df["COMPDESC"].value_counts().head(10))