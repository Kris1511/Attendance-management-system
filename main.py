import os.path
import datetime
import pickle

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import numpy as np

import util
from util import db

# from test import test


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            self._label = label
            self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        if not ret:
            print("Camera not working")
            self._label.after(20, self.process_webcam)
            return

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    # def login(self):

    #     label = test(
    #             image=self.most_recent_capture_arr,
    #             model_dir='/home/phillip/Desktop/todays_tutorial/27_face_recognition_spoofing/code/face-attendance-system/Silent-Face-Anti-Spoofing/resources/anti_spoof_models',
    #             device_id=0
    #             )

    #     if label == 1:

    def login(self):

        label = 1  

        if label == 1:

            match = util.recognize(self.most_recent_capture_arr, self.db_dir)

            if match == 'no_match':
                util.msg_box('Ups...', 'Unknown user. Please register new user or try again.')
            else:
                user_id = match['user_id']
                name = match['name']
                util.msg_box('Welcome back !', 'Welcome, {} (ID: {}).'.format(name, user_id))
                db.log_attendance(user_id, name, 'in')



        else:
            util.msg_box('Hey, you are a spoofer!', 'You are fake !')

    # def logout(self):

    #     label = test(
    #             image=self.most_recent_capture_arr,
    #             model_dir='/home/phillip/Desktop/todays_tutorial/27_face_recognition_spoofing/code/face-attendance-system/Silent-Face-Anti-Spoofing/resources/anti_spoof_models',
    #             device_id=0
    #             )

    #     if label == 1:

    def logout(self):

        label = 1 

        if label == 1:
            match = util.recognize(self.most_recent_capture_arr, self.db_dir)

            if match == 'no_match':
                util.msg_box('Ups...', 'Unknown user. Please register new user or try again.')
            else:
                user_id = match['user_id']
                name = match['name']
                util.msg_box('Hasta la vista !', 'Goodbye, {} (ID: {}).'.format(name, user_id))
                db.log_attendance(user_id, name, 'out')



        else:
            util.msg_box('Hey, you are a spoofer!', 'You are fake !')


    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=100)
        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Full Name:')
        self.text_label_register_new_user.place(x=750, y=50)

        self.entry_id_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_id_register_new_user.place(x=750, y=210)
        self.text_id_label_register_new_user = util.get_text_label(self.register_new_user_window, 'User ID:')
        self.text_id_label_register_new_user.place(x=750, y=160)


    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    # def accept_register_new_user(self):
    #     name = self.entry_text_register_new_user.get(1.0, "end-1c")

    #     # embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]
    #     embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

    #     file = open(os.path.join(self.db_dir, '{}.pickle'.format(name)), 'wb')
    #     pickle.dump(embeddings, file)

    #     util.msg_box('Success!', 'User was registered successfully !')

    #     self.register_new_user_window.destroy()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c").strip()
        user_id = self.entry_id_register_new_user.get(1.0, "end-1c").strip()

        if not name or not user_id:
            util.msg_box('Error', 'Please enter both Name and User ID.')
            return


        if not hasattr(self, 'register_new_user_capture') or self.register_new_user_capture is None:
            util.msg_box('Error', 'No image captured. Please try again.')
            return

        if os.path.exists(os.path.join(self.db_dir, f'{name}.pickle')):
            util.msg_box('Error', 'User already registered!')
            return

        frame = self.register_new_user_capture

        if frame is None or frame.size == 0:
            util.msg_box('Error', 'Empty frame. Try again.')
            return

        # Ensure image is uint8
        if frame.dtype != 'uint8':
            frame = frame.astype('uint8')

        # Ensure image is 3-channel (BGR/RGB)
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            util.msg_box('Error', 'Invalid image format. Expected 3 channels.')
            return

        # Convert to RGB for face_recognition
        rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Ensure array is C-contiguous and uint8 for dlib
        rgb_img = np.ascontiguousarray(rgb_img, dtype='uint8')

        print(f"DEBUG: rgb_img type: {type(rgb_img)}")
        print(f"DEBUG: rgb_img shape: {rgb_img.shape}")
        print(f"DEBUG: rgb_img dtype: {rgb_img.dtype}")

        try:
            encodings = face_recognition.face_encodings(rgb_img)
        except Exception as e:
            print(f"DEBUG: Face recognition failed with error: {str(e)}")
            util.msg_box('Error', f'Error during face recognition: {str(e)}')
            return

        if len(encodings) == 0:
            util.msg_box('Error', 'No face detected. Please try again.')
            return

        embeddings = encodings[0]

        try:
            success = db.register_user(user_id, name, embeddings)
            if success:
                util.msg_box('Success!', 'User registered successfully!')
                self.register_new_user_window.destroy()
            else:
                util.msg_box('Error', 'User ID already exists or database error.')

        except Exception as e:
            util.msg_box('Error', f'Error saving user data: {str(e)}')



if __name__ == "__main__":
    app = App()
    app.start()
