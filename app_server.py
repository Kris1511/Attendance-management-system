import os
import datetime
import pickle
import cv2
import numpy as np
import face_recognition
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import base64
from PIL import Image
import io

app = FastAPI()

# Enable CORS for mobile web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    return FileResponse('index.html')

DB_DIR = './db'
LOG_PATH = './log.txt'

if not os.path.exists(DB_DIR):
    os.mkdir(DB_DIR)

def decode_image(base64_string):
    try:
        # Remove header if present (e.g., "data:image/jpeg;base64,")
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        # Convert to BGR for OpenCV compatibility if needed, 
        # but face_recognition uses RGB.
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

def recognize_face(frame):
    # Convert BGR to RGB
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_img)
    
    if len(encodings) == 0:
        return None
    
    unknown_encoding = encodings[0]
    db_files = [f for f in os.listdir(DB_DIR) if f.endswith('.pickle')]
    
    best_match = "unknown"
    min_distance = 0.5 # Stricter threshold
    
    for filename in db_files:
        with open(os.path.join(DB_DIR, filename), 'rb') as f:
            known_encoding = pickle.load(f)
            distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            
            if distance < min_distance:
                min_distance = distance
                best_match = filename.replace('.pickle', '')
    
    return best_match

@app.post("/register")
async def register(name: str = Form(...), image: str = Form(...)):
    if os.path.exists(os.path.join(DB_DIR, f"{name}.pickle")):
        raise HTTPException(status_code=400, detail="User already registered!")
        
    frame = decode_image(image)
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_img)
    
    if len(encodings) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the image.")
    
    encoding = encodings[0]
    with open(os.path.join(DB_DIR, f"{name}.pickle"), 'wb') as f:
        pickle.dump(encoding, f)
    
    return {"status": "success", "message": f"User {name} registered successfully."}

@app.post("/attendance")
async def attendance(image: str = Form(...), action: str = Form(...)):
    # action should be 'in' or 'out'
    frame = decode_image(image)
    name = recognize_face(frame)
    
    if not name or name == "unknown":
        # Log unauthorized attempt
        with open(LOG_PATH, 'a') as f:
            f.write('UNKNOWN_USER,{},attempt_{}\n'.format(datetime.datetime.now(), action))
        return {"status": "error", "message": "Face not recognized. Attempt logged."}
    
    with open(LOG_PATH, 'a') as f:
        f.write('{},{},{}\n'.format(name, datetime.datetime.now(), action))
    
    return {
        "status": "success", 
        "name": name, 
        "action": action,
        "message": f"Welcome {name}!" if action == "in" else f"Goodbye {name}!"
    }

@app.get("/status")
async def get_status():
    return {"status": "online", "users_count": len(os.listdir(DB_DIR))}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
