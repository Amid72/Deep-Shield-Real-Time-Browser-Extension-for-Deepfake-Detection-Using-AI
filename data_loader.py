import numpy as np
import os
import cv2
import random
from tensorflow.keras.utils import Sequence
from PIL import Image

class HybridDataLoader(Sequence):
    """
    A robust custom Keras Sequence DataLoader that supports BOTH images and videos natively.
    Assumes data is organized as:
        data_dir/
            train/
                REAL/
                FAKE/
            val/
                REAL/
                FAKE/
    """
    def __init__(self, data_dir, split='train', img_size=(224, 224), batch_size=32, shuffle=True):
        self.data_dir = os.path.join(data_dir, split) if data_dir else None
        self.img_size = img_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        
        self.classes = {"REAL": 0, "FAKE": 1}
        
        # We'll store a list of tuples: (file_path, label, file_type)
        self.media_items = []
        
        if self.data_dir and os.path.exists(self.data_dir):
            self._load_metadata()
        else:
            print(f"[{split.upper()}] Data directory not found or empty. Using dummy data generator.")
            self.media_items = None
            
        self.on_epoch_end()

    def _load_metadata(self):
        for class_name, label in self.classes.items():
            class_dir = os.path.join(self.data_dir, class_name)
            if not os.path.exists(class_dir):
                continue
            for fname in os.listdir(class_dir):
                ext = fname.lower().split('.')[-1]
                path = os.path.join(class_dir, fname)
                if ext in ['mp4', 'avi', 'mov']:
                    self.media_items.append((path, label, 'video'))
                elif ext in ['jpg', 'jpeg', 'png']:
                    self.media_items.append((path, label, 'image'))
                    
        print(f"Found {len(self.media_items)} media items (images+videos) in {self.data_dir}")

    def __len__(self):
        if self.media_items is None:
            return 10  # Arbitrary 10 steps for dummy data
        return int(np.ceil(len(self.media_items) / self.batch_size))

    def __getitem__(self, index):
        if self.media_items is None:
            return self.generate_dummy_batch()
            
        batch_items = self.media_items[index * self.batch_size:(index + 1) * self.batch_size]
        
        X, y = [], []
        for path, label, mtype in batch_items:
            if mtype == 'image':
                frame = self.process_image(path)
                if frame is not None:
                    X.append(frame)
                    y.append(label)
            elif mtype == 'video':
                # Yield a random frame from the video to treat it as an image sample
                frame = self.extract_random_frame(path)
                if frame is not None:
                    X.append(frame)
                    y.append(label)
                
        if len(X) == 0:
             return self.generate_dummy_batch() # Failsafe
             
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32).reshape(-1, 1)

    def on_epoch_end(self):
        if self.shuffle and self.media_items is not None:
            random.shuffle(self.media_items)

    def process_image(self, img_path):
        try:
            # We use OpenCV or PIL to load image
            img = Image.open(img_path).convert('RGB')
            img = img.resize(self.img_size)
            return np.array(img) / 255.0
        except:
            return None

    def extract_random_frame(self, video_path):
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                return None
                
            # Pick a random frame index
            rand_frame_idx = random.randint(0, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, rand_frame_idx)
            
            success, frame = cap.read()
            cap.release()
            
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.img_size)
                return frame / 255.0
            return None
        except:
            return None

    def generate_dummy_batch(self):
        # NOTE: the shape is now (batch_size, 224, 224, 3) because it's image-based
        X = np.random.rand(self.batch_size, *self.img_size, 3).astype(np.float32)
        y = np.random.randint(0, 2, size=(self.batch_size, 1)).astype(np.float32)
        return X, y
