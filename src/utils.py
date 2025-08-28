import numpy as np
import pandas as pd

def season_of_month(month: int) -> str:
    if month in (12,1,2): return "DJF"
    if month in (3,4,5):  return "MAM"
    if month in (6,7,8):  return "JJA"
    return "SON"

def add_calendar_features(df: pd.DataFrame, dt_col: str = "date_time") -> pd.DataFrame:
    """Tạo các feature lịch cơ bản + season."""
    out = df.copy()
    # đảm bảo dạng datetime
    out[dt_col] = pd.to_datetime(out[dt_col])
    out["hour"] = out[dt_col].dt.hour                 # 0..23
    out["day_of_week"] = out[dt_col].dt.dayofweek     # 0..6 (Mon=0)
    out["month"] = out[dt_col].dt.month               # 1..12
    out["is_weekend"] = out["day_of_week"].isin([5, 6]).astype(int)
    out["season"] = out["month"].map(season_of_month)
    
    return out

def add_cyclical_time_features(df: pd.DataFrame, keep_original: bool = True) -> pd.DataFrame:
    out = df.copy()

    required = ["hour", "day_of_week", "month"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing calendar {missing} col. Must call add_calendar_features() before.")

    hour = out["hour"].astype(float)
    dow  = out["day_of_week"].astype(float)
    mon0 = (out["month"] - 1).astype(float) 

    out["hour_sin"]  = np.sin(2 * np.pi * hour / 24)
    out["hour_cos"]  = np.cos(2 * np.pi * hour / 24)
    out["dow_sin"]   = np.sin(2 * np.pi * dow  / 7)
    out["dow_cos"]   = np.cos(2 * np.pi * dow  / 7)
    out["month_sin"] = np.sin(2 * np.pi * mon0 / 12)
    out["month_cos"] = np.cos(2 * np.pi * mon0 / 12)

    if not keep_original:
        out = out.drop(columns=["hour", "day_of_week", "month"], axis=1)

    return out
