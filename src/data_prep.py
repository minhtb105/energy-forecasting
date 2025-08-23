import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def load_data(train_path: str, test_path: str):
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    for df in (train_df, test_df):
        df.drop(columns=["Unnamed: 0"], inplace=True, errors="ignore")
        df["zone_id"] = df["zone_id"].str.replace("zone_", "").astype(int)
    
    return train_df, test_df


def encode_season(train_df: pd.DataFrame, test_df: pd.DataFrame):
    onehot_enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

    season_encoded = onehot_enc.fit_transform(train_df[["season"]])
    season_encoded_test = onehot_enc.transform(test_df[["season"]])
    season_cols = onehot_enc.get_feature_names_out(["season"])

    df_season = pd.DataFrame(season_encoded, columns=season_cols, index=train_df.index)
    df_season_test = pd.DataFrame(season_encoded_test, columns=season_cols, index=test_df.index)

    train_df = pd.concat([train_df.drop(columns=["season"]), df_season], axis=1)
    test_df = pd.concat([test_df.drop(columns=["season"]), df_season_test], axis=1)
    
    return train_df, test_df
