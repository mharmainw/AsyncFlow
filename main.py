from fastapi import FastAPI,File,UploadFile
import csv
import io


app = FastAPI()

@app.get('/')
async def root():
    return {"message": "fuck you"}


@app.post('/upload-csv/')
async def upload(file:UploadFile = File(...)):

    if file.content_type != 'text/csv' : 
        return {"Error" : "Incorrect file type. Please upload a CSV."}
    
    contents = await file.read()
    decoded_contents = contents.decode("utf-8")

    csv_reader = csv.DictReader(io.StringIO(decoded_contents))
    data = list(csv_reader)


    return {"message" : "CSV processed successfully" , "data": data}    

