import os
import pickle

import tkinter as tk
from tkinter import messagebox
import face_recognition
import cv2
import numpy as np


def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
                        window,
                        text=text,
                        activebackground="black",
                        activeforeground="white",
                        fg=fg,
                        bg=color,
                        command=command,
                        height=2,
                        width=20,
                        font=('Helvetica bold', 20)
                    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 21), justify="left")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=2,
                       width=15, font=("Arial", 32))
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)


def recognize(img, db_path):
    # it is assumed there will be at most 1 match in the db

    if img is None or img.size == 0:
        return 'no_persons_found'

    # Ensure image is uint8
    if img.dtype != 'uint8':
        img = img.astype('uint8')

    # Convert to RGB for face_recognition
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Ensure array is C-contiguous and uint8 for dlib
    rgb_img = np.ascontiguousarray(rgb_img, dtype='uint8')

    print(f"DEBUG RECOGNIZE: rgb_img type: {type(rgb_img)}")
    print(f"DEBUG RECOGNIZE: rgb_img shape: {rgb_img.shape}")
    print(f"DEBUG RECOGNIZE: rgb_img dtype: {rgb_img.dtype}")

    try:
        embeddings_unknown = face_recognition.face_encodings(rgb_img)
    except Exception as e:
        print(f"DEBUG RECOGNIZE: Face recognition failed with error: {str(e)}")
        return 'no_persons_found'

    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted([f for f in os.listdir(db_path) if f.endswith('.pickle')])

    best_match_name = 'unknown_person'
    min_distance = 0.5  # Tolerance threshold (Lower is stricter)

    for filename in db_dir:
        path_ = os.path.join(db_path, filename)
        with open(path_, 'rb') as file:
            known_embeddings = pickle.load(file)
            
            # Calculate distance (lower means more similar)
            distances = face_recognition.face_distance([known_embeddings], embeddings_unknown)
            
            if distances[0] < min_distance:
                min_distance = distances[0]
                best_match_name = filename[:-7]

    return best_match_name

