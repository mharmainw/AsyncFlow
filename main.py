from fastapi import FastAPI,File,UploadFile
import csv
import io
from enum import Enum




app = FastAPI()

@app.get('/')
async def root():
    return {"message": "fuck you"}

class MissingPolicy(Enum):
    PRESERVE  = 'preserve'
    DROP_ROWS = 'drop_rows' # drop for row if any missing value 
    DROP_REQUIRED = 'drop_required' # drop row if required values are missing 


@app.post('/Job/')
async def Job(file:UploadFile = File(...), required_columns:list[str] = [], missing_value_policy: MissingPolicy = ['preserve']):

    if file.content_type != 'text/csv' : 
        return {"Error" : "Incorrect file type. Please upload a CSV."}
    
    contents = await file.read()
    decoded_contents = contents.decode("utf-8")

    csv_reader = csv.DictReader(io.StringIO(decoded_contents))
    data = list(csv_reader)


    return {"message" : "CSV processed successfully" , "data": data}    

