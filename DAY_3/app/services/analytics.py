import pandas as pd
import os
def load_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def Summary(df: pd.DataFrame):
    return{
        "rows" : df.shape[0],
        "coloums": df.shape[1],
        "coloums_type": df.dtypes.astype(str).to_dict()
    } 

def missing_values(df: pd.DataFrame):
    return {
        "missing_values":df.isnull().sum().to_dict()
    }

def corelation_matrix(df : pd.DataFrame):
    num_df = df.select_dtypes(include="number")
    return{
        "corelation": num_df.corr().fillna(0).to_dict()
        }