import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from bot.engine import GameEngine

app = FastAPI()
engine = GameEngine()

app.mount("/static", StaticFiles(directory="web/static"), name="static")

connections = set()

@app.get("/")
async def index():
    with open("web/templates/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.add(ws)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        connections.remove(ws)

async def broadcast(state):
    for ws in list(connections):
        try:
            await ws.send_json(state)
        except:
            connections.remove(ws)

@app.on_event("startup")
async def startup_event():
    engine.register_listener(broadcast)
    asyncio.create_task(engine.run())
