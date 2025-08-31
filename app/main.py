from fastapi import FastAPI, WebSocket, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from starlette.responses import Response
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

@app.get("/debug")
async def debug():
    return "<center>hello world</center>"

@app.websocket("/socket/")
async def sock(sock:WebSocket):
    await sock.accept()

    while True:
        data = await sock.receive_text()
        await sock.send_text(f"got: {data}")
        print(data)
