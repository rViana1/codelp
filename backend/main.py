from fastapi import FastAPI

app = FastAPI(
    title="Codelp",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Codelp!"
    }