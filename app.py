from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import random
from PIL import Image
import io
import os
import cv2
import tempfile
import tensorflow as tf
import numpy as np

app = FastAPI()

# Enable CORS for the chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model if available
MODEL_PATH = "../model/deepshield_mobilenet_image.h5"
try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        model = None
        print("Model file not found. Running in dummy mode.")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

IMG_SIZE = (224, 224)
FRAME_COUNT = 20  # Number of frames to sample for video classification

def preprocess_image(image: Image.Image):
    """Preprocess single image for the MobileNetV2 image model."""
    img = image.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0  # Normalize
    
    # Return shape (1, 224, 224, 3)
    return np.expand_dims(img_array, axis=0)

def extract_frames(video_path, num_frames=20):
    """Extract frames from video and return as a batch of independent images."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    
    if total_frames > 0:
        step = max(total_frames // num_frames, 1)
        for i in range(num_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
            success, frame = cap.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, IMG_SIZE)
                frames.append(frame / 255.0)
            else:
                break
    cap.release()
    
    if len(frames) == 0:
        return None
        
    sequence = np.array(frames)
    # Return shape (num_frames, 224, 224, 3)
    # The model will evaluate each frame independently
    return sequence

@app.get("/")
def home():
    return {"status": "DeepShield Backend Running", "model_loaded": model is not None}

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert('RGB')
    except:
        return JSONResponse(content={"error": "Invalid image"}, status_code=400)

    if model:
        try:
            input_tensor = preprocess_image(image)
            prediction = model.predict(input_tensor, verbose=0)[0][0]
            is_fake = float(prediction) > 0.5
            confidence = float(prediction) if is_fake else 1.0 - float(prediction)
        except Exception as e:
            return JSONResponse(content={"error": f"Model inference error: {str(e)}"}, status_code=500)
    else:
        # Dummy detection fallback
        is_fake = random.random() < 0.3
        confidence = round(random.uniform(0.7, 0.99), 2)

    return {
        "media_type": "image",
        "result": "FAKE" if is_fake else "REAL",
        "confidence": confidence
    }

@app.post("/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    # Save uploaded video to temp file for OpenCV processing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        content = await file.read()
        temp_video.write(content)
        temp_video_path = temp_video.name
        
    try:
        if model:
            input_tensor = extract_frames(temp_video_path, num_frames=FRAME_COUNT)
            if input_tensor is None:
                return JSONResponse(content={"error": "Could not extract video frames"}, status_code=400)
                
            # Predict entirely independent frames then average the confidence scores
            predictions = model.predict(input_tensor, verbose=0).flatten()
            avg_prediction = np.mean(predictions)
            
            is_fake = float(avg_prediction) > 0.5
            confidence = float(avg_prediction) if is_fake else 1.0 - float(avg_prediction)
        else:
            # Dummy detection fallback
            is_fake = random.random() < 0.3
            confidence = round(random.uniform(0.7, 0.99), 2)
    except Exception as e:
        return JSONResponse(content={"error": f"Video analysis error: {str(e)}"}, status_code=500)
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

    return {
        "media_type": "video",
        "result": "FAKE" if is_fake else "REAL",
        "confidence": confidence
    }
