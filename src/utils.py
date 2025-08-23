import pandas as pd

def season_of_month(month: int) -> str:
    if month in (12,1,2): return "DJF"
    if month in (3,4,5):  return "MAM"
    if month in (6,7,8):  return "JJA"
    
    return "SON"

def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df["hour"] = df["date_time"].dt.hour
    df["day_of_week"] = df["date_time"].dt.dayofweek
    df["month"] = df["date_time"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5,6]).astype(int)
    df["season"] = df["month"].map(season_of_month)
    
    return df
