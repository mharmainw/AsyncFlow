import numpy as np
import pandas as pd
import csv
from enum import Enum

class MissingPolicy(Enum):
    PRESERVE  = 'preserve'
    DROP_ROWS = 'drop_rows' # drop for row if any missing value 
    DROP_REQUIRED = 'drop_required' # drop row if required values are missing 

def clean(filename:str,required_cols:list[str],Policy:MissingPolicy = MissingPolicy.PRESERVE ):
    df = pd.read_csv(filename)

    columns = [column for column in df.columns]

    print(columns)

    for x in required_cols:
        if x not in columns:
            raise ValueError("Missing required columns")

    
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.drop_duplicates()



    

    if Policy == MissingPolicy.PRESERVE:
        pass
    
    elif Policy == MissingPolicy.DROP_ROWS:
        df = df.dropna()

    elif Policy == MissingPolicy.DROP_REQUIRED:
        df = df.dropna(subset= required_cols)

    else:
        print("This Policy Does Not Exist")

    

    return df

def statistics(filename:str):
    df = pd.read_csv(filename)

    
    



