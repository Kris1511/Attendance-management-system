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

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])

        file = open(path_, 'rb')
        embeddings = pickle.load(file)

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'

