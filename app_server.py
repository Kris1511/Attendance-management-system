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
from db_manager import DatabaseManager

db = DatabaseManager()


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
    known_users = db.get_all_users()
    
    best_match = None
    min_distance = 0.5 # Stricter threshold
    
    for user in known_users:
        distance = face_recognition.face_distance([user['encoding']], unknown_encoding)[0]
        
        if distance < min_distance:
            min_distance = distance
            best_match = {'user_id': user['user_id'], 'name': user['name']}
    
    return best_match



@app.post("/register")
async def register(user_id: str = Form(...), name: str = Form(...), image: str = Form(...)):
    frame = decode_image(image)
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_img)
    
    if len(encodings) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the image.")
    
    encoding = encodings[0]
    success = db.register_user(user_id, name, encoding)
    
    if not success:
        raise HTTPException(status_code=400, detail="User ID already exists or database error.")
    
    return {"status": "success", "message": f"User {name} (ID: {user_id}) registered successfully."}



@app.post("/attendance")
async def attendance(image: str = Form(...), action: str = Form(...)):
    # action should be 'in' or 'out'
    frame = decode_image(image)
    match = recognize_face(frame)
    
    if not match:
        return {"status": "error", "message": "Face not recognized."}
    
    user_id = match['user_id']
    name = match['name']
    db.log_attendance(user_id, name, action)
    
    return {
        "status": "success", 
        "user_id": user_id,
        "name": name, 
        "action": action,
        "message": f"Welcome {name}!" if action == "in" else f"Goodbye {name}!"
    }



@app.get("/status")
async def get_status():
    return {"status": "online", "users_count": len(os.listdir(DB_DIR))}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
