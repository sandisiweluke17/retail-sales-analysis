import pandas as pd


def load_data(path="data/sales_data.csv"):
    """Read the raw CSV exactly as it is."""
    return pd.read_csv(path)


def clean_data(df):
    """Fix every known problem in code and return (clean_df, report)."""
    df = df.copy()
    report = {"rows_start": len(df)}

    # 1. Inconsistent text: strip spaces, standardise capitalisation
    for col in ["category", "store"]:
        df[col] = df[col].str.strip().str.title()
    df["product_name"] = df["product_name"].str.strip()
    df["payment_method"] = df["payment_method"].str.strip()

    # 2. Dates: ISO first, then the US-style fallback (03/15/2026)
    iso = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    us = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="coerce")
    report["dates_reformatted"] = int((iso.isna() & us.notna()).sum())
    df["date"] = iso.fillna(us)

    # 3. Numbers: bad values ("unknown") become NaN
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # 4. Drop missing quantity
    before = len(df)
    df = df.dropna(subset=["quantity"])
    report["missing_quantity"] = before - len(df)

    # 5. Drop missing / non-numeric price
    before = len(df)
    df = df.dropna(subset=["unit_price"])
    report["bad_price"] = before - len(df)

    # 6. Drop impossible negative quantities
    before = len(df)
    df = df[df["quantity"] > 0]
    report["negative_quantity"] = before - len(df)

    # 7. Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates"] = before - len(df)

    # 8. Revenue (the first piece of analysis)
    df["revenue"] = df["quantity"] * df["unit_price"]

    report["rows_clean"] = len(df)
    return df.reset_index(drop=True), report


def print_quality_report(report):
    """Print the data-quality report."""
    removed = report["rows_start"] - report["rows_clean"]
    print("DATA-QUALITY REPORT")
    print("-" * 40)
    print(f"Rows at start:              {report['rows_start']}")
    print(f"Removed - missing quantity: {report['missing_quantity']}")
    print(f"Removed - bad/unknown price:{report['bad_price']}")
    print(f"Removed - negative quantity:{report['negative_quantity']}")
    print(f"Removed - duplicates:       {report['duplicates']}")
    print(f"Total removed:              {removed}")
    print(f"Dates reformatted:          {report['dates_reformatted']}")
    print(f"Clean rows remaining:       {report['rows_clean']}")