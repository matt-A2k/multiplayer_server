from fastapi import FastAPI

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<center><h1>hello world</h1></center>"
