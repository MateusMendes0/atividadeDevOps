from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Atividade DevOps", version="1.0.0")


@app.get("/hello", response_class=PlainTextResponse)
def hello() -> str:
    return "Hello World"
