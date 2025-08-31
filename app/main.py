from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
import asyncio
import json
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

CSP = "default-src 'none'; connect-src 'self' wss://multiplayer-server-b8bb.onrender.com; script-src 'self'; style-src 'self';"
@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    resp = await call_next(request)
    # Only add for HTML responses (optional)
    if resp.headers.get("content-type", "").startswith("text/html"):
        resp.headers["Content-Security-Policy"] = CSP
    return resp

@app.get("/debug")
async def debug():
    return "<center>hello world</center>"

@app.get('/view/{game}')
async def test(game:str):
    if not game in games.keys():return "No Connections"
    return(games[game]['players'])

games = {}

@app.websocket("/0/{game_name}/{player_name}/{game_password}")
async def game_socket(sock:WebSocket, game_name:str, player_name:str, game_password:str):

    disconnect = False

    # perform checks before attempting to connect
    if(game_name in games):
        if(games[game_name]['password']!=game_password):
            await sock.close(reason='incorrect password to existing game')
#            print('incorrect password')
            disconnect = True
        elif(player_name in games[game_name]['players']):
            await sock.close(reason='player name already exists')
#            print('name exists')
            disconnect = True
    else:games[game_name] = {'password':game_password, 'player_send':{}, 'players':{}}

    await sock.accept()
    if(disconnect):return
#       print(f"{player_name} joined {game_name}")

    games[game_name]['players'][player_name] = ''
    games[game_name]['player_send'][player_name] = asyncio.Event()

    async def send():
        while game_name in games:
            await games[game_name]['player_send'][player_name].wait()
            await sock.send_text(json.dumps(games[game_name]['players']))
            games[game_name]['player_send'][player_name].clear()

    async def recv():
        while True:
            data = await sock.receive_text()
            if(data!=''):games[game_name]['players'][player_name]=data
            for player in games[game_name]['player_send'].keys():
                games[game_name]['player_send'][player].set()

    try:
        # main code that gets run in a loop if everything above works sucessfully
        await asyncio.gather(recv(), send())
    except Exception as e:
        del games[game_name]['players'][player_name]
        del games[game_name]['player_send'][player_name]
        if(len(games[game_name]['players'])==0):del games[game_name]
