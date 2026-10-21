import pandas as pd
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
        raise ValueError("No such policy exists")

    

    return df

def statistics(filename:str):
    df = pd.read_csv(filename)

    #columns
    features = df.columns.tolist()
    # print(f'Column names: {features}')

    #row number
    noofrows = len(df)
    # print(f'no of rows: {noofrows}')

    #col number
    noofcols = len(df.columns)
    # print(f'no of columns: {noofcols}')
    
    # duplicates
    df_nodup = df.drop_duplicates()
    duplicates = len(df)-len(df_nodup)

    # print(f'no of duplicate rows: {duplicates}')


    #data_types 
    datatypes =df.dtypes.astype('str').to_dict()

    # print(datatypes)


    #missing values per col

    missing_values = {}
    for x in features:
        missing_values[x] = int(df[x].isna().sum())


    # print(missing_values) 

    final_answer = {
        'row_count': noofrows,
        'column_count': noofcols,
        'columns': features,
        'missing_values_by_column': missing_values,
        'duplicate_rows': duplicates,
        'data_types': datatypes
    }

    return final_answer



