import pyaudio
import wave
import threading
import datetime
import os
import time 
import tkinter as tk
from tkinter import messagebox
from tkinter import *

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORDING = False
PAUSED = False
frames = []
start_time = None
elapsed_time = 0
audio = pyaudio.PyAudio()
playback_stream = None

# Ensure recordings directory exists
if not os.path.exists("recordings"):
    os.makedirs("recordings")

# Function to start, pause, or resume recording
def toggle_recording():
    global RECORDING, PAUSED, frames, start_time, elapsed_time

    if not RECORDING:
        RECORDING = True
        PAUSED = False
        frames = []
        start_time = time.time()
        elapsed_time = 0
        update_timer()
        threading.Thread(target=record).start()
        start_pause_button.config(text="⏸ Pause", fg="blue")
    elif PAUSED:
        PAUSED = False
        start_time = time.time() - elapsed_time
        update_timer()
        start_pause_button.config(text="⏸ Pause", fg="blue")
    else:
        PAUSED = True
        start_pause_button.config(text="▶ Resume", fg="green")

# Function to stop recording
def stop_recording():
    global RECORDING
    if RECORDING:
        RECORDING = False
        save_recording()
        start_pause_button.config(text="▶ Start", fg="black")
        timer_label.config(text="00:00")

# Function to handle audio recording
def record():
    global RECORDING, PAUSED, frames

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while RECORDING:
        if not PAUSED:
            data = stream.read(CHUNK)
            frames.append(data)
    stream.stop_stream()
    stream.close()

# Timer function
def update_timer():
    global elapsed_time
    if RECORDING and not PAUSED:
        elapsed_time = int(time.time() - start_time)
        minutes, seconds = divmod(elapsed_time, 60)
        timer_label.config(text=f"{minutes:02}:{seconds:02}")
        root.after(1000, update_timer)

# Function to save the recorded file
def save_recording():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"recordings/recording_{timestamp}.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    messagebox.showinfo("Saved", f"Recording saved as {filename}")
    update_recordings()

# Function to update list of recordings
def update_recordings():
    for widget in recordings_frame.winfo_children():
        widget.destroy()

    files = sorted(os.listdir("recordings"), reverse=True)

    for file in files:
        if file.endswith(".wav"):
            frame = tk.Frame(recordings_frame)
            frame.pack(fill="x", padx=10, pady=2)

            label = tk.Label(frame, text=file, font=("Arial", 10), width=30, anchor="w")
            label.pack(side="left")

            play_btn = tk.Button(frame, text="▶", command=lambda f=file: play_audio(f), width=3)
            play_btn.pack(side="left", padx=5)

            pause_btn = tk.Button(frame, text="⏸", command=stop_audio, width=3)
            pause_btn.pack(side="left", padx=5)

            delete_btn = tk.Button(frame, text="🗑", command=lambda f=file: delete_recording(f), width=3)
            delete_btn.pack(side="left", padx=5)

# Function to play audio
def play_audio(filename):
    global playback_stream
    wf = wave.open(f"recordings/{filename}", 'rb')
    playback_stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

    def play():
        global playback_stream
        data = wf.readframes(CHUNK)
        while data and playback_stream.is_active():
            playback_stream.write(data)
            data = wf.readframes(CHUNK)
        stop_audio()

    threading.Thread(target=play).start()

# Function to stop playback
def stop_audio():
    global playback_stream
    if playback_stream:
        playback_stream.stop_stream()
        playback_stream.close()
        playback_stream = None

# Function to delete a recording
def delete_recording(filename):
    os.remove(f"recordings/{filename}")
    update_recordings()
    messagebox.showwarning("WARNING!",message="Are you sure of this action?")
    messagebox.showinfo("Deleted", f"{filename} has been deleted.")

# GUI setup
root = tk.Tk()
root.title("Voice Recorder")
root.geometry("400x800")
root.configure(background="#4a4a4a")

#icon
image_icon=PhotoImage(file="Record.png")
root.iconphoto(False,image_icon)

# Title label
title_label = tk.Label(root, text="🎤Voice Recorder", font=("Arial", 16, "bold"), background="#4a4a4a")
title_label.pack(pady=3)

# Load image
photo = tk.PhotoImage(file="Record.png")  # Only supports PNG and GIF

# Create button with image
button = tk.Button(root, text="Click Me", command=toggle_recording, image=photo,background="#4a4a4a")
button.pack(padx=5, pady=5)


# Timer display
timer_label = tk.Label(root, text="00:00", font=("Arial", 14, "bold"))
timer_label.pack(pady=5)

# Start/Pause button
start_pause_button = tk.Button(root, text="▶ Start", command=toggle_recording, font=("Arial", 14))
start_pause_button.pack(pady=5)

# Stop button
stop_button = tk.Button(root, text="⏹ Stop", command=stop_recording, fg="black", font=("Arial", 14))
stop_button.pack(pady=5)

# Recordings section label
recordings_label = tk.Label(root, text="Previous Records", font=("Arial", 12, "bold"))
recordings_label.pack(pady=5)

# Frame to hold recording list
recordings_frame = tk.Frame(root)
recordings_frame.pack(fill="both", expand=True)

# Scrollable Frame for Recordings
recordings_canvas = tk.Canvas(root, height=350)
recordings_scroll = tk .Scrollbar(root, orient="vertical", command=recordings_canvas.yview)
recordings_frame = tk.Frame(recordings_canvas)
recordings_frame.pack(fill="x", expand=True)

recordings_frame.bind("<Configure>", lambda e: recordings_canvas.configure(scrollregion=recordings_canvas.bbox("all")))
recordings_window = recordings_canvas.create_window((0, 0), window=recordings_frame, anchor="nw")

recordings_canvas.configure(yscrollcommand=recordings_scroll.set)

recordings_canvas.pack(side="left", fill="both", expand=True)
recordings_scroll.pack(side="right", fill="y")

# Load existing recordings  
update_recordings()

# Run the GUI
root.mainloop()
audio.terminate()