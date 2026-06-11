# src/main_server.py
import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Connect root path for configurations and simulator imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logistics_config import SERVER_HOST, SERVER_PORT
from src.fleet_simulator import FleetSimulator

app = FastAPI(title="Supply Chain Optimization & Dispatch Lab")

# Setup template routing engines
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Initialize our background fleet tracker engine
simulator = FleetSimulator()

@app.get("/", response_class=HTMLResponse)
async def serve_logistics_hub(request: Request):
    """Serves the central operations research control tower mapping interface"""
    return templates.TemplateResponse(request, name="logistics_hub.html")

@app.websocket("/ws/fleet-stream")
async def stream_live_fleet_telemetry(websocket: WebSocket):
    """Bridges the backend greedy heuristic tracking loop with client web elements"""
    await websocket.accept()
    print("🔌 Operations Control Center connected to live fleet websocket pipeline.")
    
    try:
        # Loop through our asynchronous telemetry stream generator
        async for telemetry_packet in simulator.stream_fleet_telemetry():
            # Send the live telemetry metrics down the pipe to our UI
            await websocket.send_json(telemetry_packet)
            
    except WebSocketDisconnect:
        print("🔌 Operations Control Center closed the session telemetry pipeline.")
    except Exception as e:
        print(f"❌ Critical error in websocket pipeline channel thread: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass # Socket already closed cleanly

# Optimized script execution block
if __name__ == "__main__":
    import uvicorn
    print("⏳ Awakening Logistics Network Router & Control Tower Server...")
    print(f"🌐 Management portal address active at: http://{SERVER_HOST}:{SERVER_PORT}")
    
    # Run the server module bound cleanly to your designated standalone port configuration
    uvicorn.run("src.main_server:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)