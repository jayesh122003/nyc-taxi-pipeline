import pandas as pd

def clean_financial_values(df):
    """Remove rows with negative values in any numeric column."""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    mask = (df[numeric_cols] >= 0).all(axis=1)
    return df[mask]

def clean_datetime(df, year=2024, month=1):
    """Remove invalid datetime rows and add trip_duration_mins column."""
    df = df.copy()
    df['trip_duration_mins'] = (
        df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    ).dt.total_seconds() / 60

    mask = (
        (df['tpep_pickup_datetime'].dt.year == year) &
        (df['tpep_pickup_datetime'].dt.month == month) &
        (df['trip_duration_mins'] > 0) &
        (df['trip_duration_mins'] <= 600)
    )
    return df[mask]


def clean_trip_values(df):
    """Remove rows with invalid passenger_count(passenger_count = 0 or > 6) and invalid trip_distance"""
    # NYC legal taxi limit is 6 passengers (rate code 6 allows group rides)
    mask = ((df['passenger_count'] != 0) & (df['passenger_count'] <= 6) & (df['trip_distance'] > 0) & (df['trip_distance'] < 100))
    return df[mask]


def fix_datatypes(df: pd.DataFrame):

    df = df.copy()
    df['passenger_count'] = df['passenger_count'].astype(int)
    df['RatecodeID'] = df['RatecodeID'].astype(str)
    df['payment_type'] = df['payment_type'].astype(str)
    df.columns = df.columns.str.lower()

    return df


def transform(df):
    print(f"Starting rows: {len(df):,}")
    df = clean_financial_values(df)
    print(f"After clean_financial_values: {len(df):,} rows")
    df = clean_datetime(df)
    print(f"After clean_datetime: {len(df):,} rows")
    df = clean_trip_values(df)
    print(f"After clean_trip_values: {len(df):,} rows")
    df = fix_datatypes(df)
    print(f"After fix_datatypes: {len(df):,} rows")
    return df



if __name__ == '__main__':
    from extract import load_raw_data
    df = load_raw_data()
    df = transform(df)

