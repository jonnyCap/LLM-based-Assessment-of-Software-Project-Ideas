from fastapi import FastAPI

app = FastAPI()

@app.get("/api/hello-world")
def read_root():
    return {"message": "Hello, FastAPI!"}
