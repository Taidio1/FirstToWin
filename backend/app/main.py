from fastapi import FastAPI

app = FastAPI(title="NDR Project API")

@app.get("/")
async def root():
    return {"message": "Welcome to NDR Project API"}
