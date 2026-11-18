import pandas as pd

ZIP_PATH = "FLAT_CMPL.zip"
START = "2015-01-01"
MONTHS_TO_DROP = 3
MIN_TOTAL = 100
KEYS = ["MAKETXT", "MODELTXT", "SYSTEM"]

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

COLUMNS = {
    0: "CMPLID",
    3: "MAKETXT",
    4: "MODELTXT",
    7: "FAILDATE",
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

df["FAILDATE"] = pd.to_datetime(df["FAILDATE"], format="%Y%m%d", errors="coerce")
df["DATEA"] = pd.to_datetime(df["DATEA"], format="%Y%m%d", errors="coerce")

last_added = df["DATEA"].max()
end_month = (last_added.to_period("M") - MONTHS_TO_DROP).to_timestamp()
print("Last DATEA:", last_added.date())
print("Counting from", START, "to", end_month.date(), "(last months skipped: incomplete)")

for col in ["MAKETXT", "MODELTXT", "COMPDESC"]:
    df[col] = df[col].fillna("").str.strip().str.upper()
df["SYSTEM"] = df["COMPDESC"].str.split(":").str[0].str.strip()

keep = (
    df["FAILDATE"].notna()
    & (df["FAILDATE"] >= START)
    & (df["FAILDATE"] < end_month + pd.offsets.MonthBegin(1))
    & ~df["MAKETXT"].isin(["", "UNKNOWN"])
    & ~df["MODELTXT"].isin(["", "UNKNOWN"])
    & (df["SYSTEM"] != "")
)
df = df[keep].copy()
print("Complaints used:", len(df))

df["month"] = df["FAILDATE"].dt.to_period("M").dt.to_timestamp()
counts = df.groupby(KEYS + ["month"]).size().rename("n").reset_index()

totals = counts.groupby(KEYS)["n"].sum().rename("total").reset_index()
eligible = totals[totals["total"] >= MIN_TOTAL][KEYS]
print("All groups:", len(totals))
print(f"Groups with at least {MIN_TOTAL} complaints:", len(eligible))

counts_e = counts.merge(eligible, on=KEYS)
share = counts_e["n"].sum() / counts["n"].sum()
print(f"Share of complaints covered by these groups: {share:.1%}")

pivot = counts_e.pivot_table(index=KEYS, columns="month", values="n", aggfunc="sum", fill_value=0)
all_months = pd.date_range(START, end_month, freq="MS")
pivot = pivot.reindex(columns=all_months, fill_value=0)
pivot.columns.name = "month"

active = (pivot > 0).sum(axis=1)
print("Months in the window:", len(all_months))
print("Groups active in at least 24 months:", (active >= 24).sum())
print("Groups active in at least 60 months:", (active >= 60).sum())

long = pivot.stack().rename("complaints").reset_index()
long.to_csv("group_monthly_counts.csv", index=False)
print("Saved group_monthly_counts.csv with", len(long), "rows")

top = totals.merge(eligible, on=KEYS).sort_values("total", ascending=False).head(15)
print("\nTop 15 groups:")
print(top.to_string(index=False))
