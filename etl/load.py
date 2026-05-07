import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    return engine

def load(df):
    """Load clean dataframe into PostgreSQL."""
    engine = get_engine()

    print(f"Loading {len(df):,} rows into PostgreSQL...")
    df.to_sql('taxi_trips', engine, if_exists='replace', index=False)
    print("Done.")

def load_zones(df):
    """"Load tazi zone lookup dataframe into PostgreSQL."""

    engine = get_engine()

    print(f"Loading {len(df):,} rows into PostgreSQL...")
    df.to_sql('zone_lookup', engine, if_exists='replace', index=False)
    print("Done.")

if __name__ == '__main__':
    from extract import load_raw_data
    from extract import load_zone_lookup
    df1 = load_raw_data()
    df2 = load_zone_lookup()
    from transform import transform
    df1 = transform(df1)
    load(df1)
    load_zones(df2)





