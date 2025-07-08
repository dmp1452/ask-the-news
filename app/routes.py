from fastapi import FastAPI

app = FastAPI
@app.get('/ask')
def ask():
    return {"message": "TBD"}
