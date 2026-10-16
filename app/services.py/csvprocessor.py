import numpy as np
import pandas as pd
import csv
from enum import Enum

class MissingPolicy(Enum):
    PRESERVE  = 'preserve'
    DROP_ROWS = 'drop_rows' # drop for row if any missing value 
    DROP_REQUIRED = 'drop_required' # drop row if required values are missing 

def clean(filename:str,Policy:MissingPolicy,required_cols:list[str]):
    df = pd.read_csv(filename)

    columns = [column for column in df.columns]

    if required_cols not in columns:
        raise ValueError("Missing required columns")

    df.drop_duplicates()

    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    

    if Policy.PRESERVE:
        pass
    
    elif Policy.DROPROWS:
        df.dropna()

    elif Policy.DROP_REQUIRED:
        df.dropna(subset= required_cols)

    else:
        print("This Policy Does Not Exist")

    return df

def statistics(filename:str):
    df = pd.read_csv(filename)
    
