"""Starter for House Prices & the Economy, November 2026: Booms and busts.

Works with the "Average prices" attribute file or the UK HPI full file.

Usage:
    python3 starter.py Average-prices-2026-08.csv "London"

Prints a quick summary for the region and saves a line chart of average prices.
"""

import sys

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python3 starter.py <csv> ["Region name"]')
        sys.exit(1)

    csv_path = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "United Kingdom"

    df = pd.read_csv(csv_path, low_memory=False)
    # The attribute files use Region_Name / Average_Price, the full file uses RegionName / AveragePrice.
    df = df.rename(columns={"RegionName": "Region_Name", "AveragePrice": "Average_Price"})
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False, errors="coerce")

    subset = df[df["Region_Name"].str.lower() == region.lower()].sort_values("Date")
    if subset.empty:
        print(f"No rows found for '{region}'. A few region names to try:")
        print(", ".join(sorted(df["Region_Name"].dropna().unique())[:20]))
        sys.exit(1)

    latest = subset.iloc[-1]
    print(f"Region:        {region}")
    print(f"Rows:          {len(subset):,}")
    print(f"Date range:    {subset['Date'].min():%b %Y} to {subset['Date'].max():%b %Y}")
    print(f"Latest price:  £{latest['Average_Price']:,.0f} ({latest['Date']:%b %Y})")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(subset["Date"], subset["Average_Price"], linewidth=2)
    ax.set_title(f"Average house price: {region}")
    ax.set_ylabel("Average price (£)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"£{v:,.0f}"))
    ax.grid(alpha=0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.text(0.01, 0.01, "Source: HM Land Registry UK HPI, OGL v3.0", fontsize=8, alpha=0.6)
    fig.tight_layout()

    out = f"{region.lower().replace(' ', '-')}-average-price.png"
    fig.savefig(out, dpi=150)
    print(f"Saved chart:   {out}")


if __name__ == "__main__":
    main()
