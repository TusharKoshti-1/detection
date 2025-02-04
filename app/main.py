from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
from app.detection.face_detector import FaceMeshDetector
from app.utils.tracker import EyeTracker

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

detector = FaceMeshDetector()
tracker = EyeTracker()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # Convert the received bytes into an image frame.
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                continue
            # Process the frame: run detection and draw bounding boxes.
            # Inside your WebSocket loop (example)
            ear, landmarks = detector.process_frame(frame)
            if landmarks is not None:
                frame = detector.draw_landmarks(frame, landmarks, ear)

            # Encode the processed frame as JPEG with quality 70.
            _, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            await websocket.send_bytes(jpeg.tobytes())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()