import pyaudio
import wave
import threading
import datetime
import os
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk
import ttkbootstrap as tb  # Bootstrap-like themes
from ttkbootstrap import Style

print("✅ All required libraries are installed!")

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
    
is_playing = False  # Track whether audio is playing or paused

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
        start_pause_button.config(text="⏸ Pause", bootstyle="warning")
    elif PAUSED:
        PAUSED = False
        start_time = time.time() - elapsed_time
        update_timer()
        start_pause_button.config(text="⏸ Pause", bootstyle="warning")
    else:
        PAUSED = True
        start_pause_button.config(text="▶ Resume", bootstyle="success")

# Function to stop recording
def stop_recording():
    global RECORDING
    if RECORDING:
        RECORDING = False
        save_recording()
        start_pause_button.config(text="▶ Start", bootstyle="primary")
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
    global frames

    # Ask the user to enter a name
    name = simpledialog.askstring("Save Recording", "Enter recording name:")
    if not name:  # If the user cancels or enters nothing, use a default name
        name = "Untitled"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"recordings/{name}_{timestamp}.wav"

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    messagebox.showinfo("Saved", f"Recording '{name}' saved successfully.")
    update_recordings()  # Refresh recordings list

# Function to update list of recordings
def update_recordings():
    for widget in recordings_frame.winfo_children():
        widget.destroy()

    files = sorted(os.listdir("recordings"), reverse=True)

    for file in files:
        if file.endswith(".wav"):
            frame = tb.Frame(recordings_frame, bootstyle="light", padding=5)
            frame.pack(fill="x", padx=5, pady=3)

            # Extract Name & Date from filename (Format: name_YYYY-MM-DD_HH-MM-SS.wav)
            name, date_time = file.rsplit("_", 1)
            date_time = date_time.replace(".wav", "").replace("_", " ")  # Convert timestamp to readable format

            # Label for Name
            name_label = tb.Label(frame, text=name, font=("Arial", 10, "bold"))
            name_label.pack(side="left", padx=5)

            # Label for Date & Time
            date_label = tb.Label(frame, text=date_time, font=("Arial", 8), bootstyle="secondary")
            date_label.pack(side="left", padx=5)

            play_btn = tb.Button(frame, text="▶", bootstyle="success-outline", command=lambda f=file: play_audio(f))
            play_btn.pack(side="right", padx=2)

            #pause_btn = tk.Button(frame, text="⏸", command=lambda: stop_audio(), width=3)
            #pause_btn.pack(side="left", padx=5)

            delete_btn = tb.Button(frame, text="🗑", bootstyle="danger-outline", command=lambda f=file: delete_recording(f))
            delete_btn.pack(side="right", padx=2)

            # Pass play_btn to play_audio
            play_btn.config(command=lambda f=file, btn=play_btn: play_audio(f, btn))

# Function to play audio
# Add this at the top of your script to initialize variables
current_play_btn = None  # Track which button is controlling playback
is_playing = False  # Track playback state
paused = False  # Track paused state
paused_data = None  # Store paused audio data
playback_stream = None  # Store playback stream

def play_audio(filename, play_btn):
    global playback_stream, is_playing, current_play_btn, paused, paused_data

    # If clicking the same button, toggle pause/play
    if current_play_btn == play_btn:
        if is_playing:  # Pause if playing
            is_playing = False
            paused = True
            play_btn.config(text="▶")  # Change button back to play
            status_label.config(text="Paused ⏸", style="Orange.TLabel")
            return
        elif paused:  # Resume if paused
            is_playing = True
            paused = False
            play_btn.config(text="⏸")  # Change button to pause
            status_label.config(text=f"Playing: {filename} 🎵", style="Green.TLabel")
            threading.Thread(target=resume_playback, daemon=True).start()
            return

    # Stop previous playback if a different file is clicked
    if is_playing:
        is_playing = False  # Stop current playback
        if playback_stream:
            playback_stream.stop_stream()
            playback_stream.close()
            playback_stream = None
        if current_play_btn:
            current_play_btn.config(text="▶")  # Reset previous button

    # Start playing new audio
    current_play_btn = play_btn
    status_label.config(text=f"Playing: {filename} 🎵", style="Green.TLabel")

    wf = wave.open(f"recordings/{filename}", 'rb')
    playback_stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

    is_playing = True
    paused = False
    paused_data = wf  # Store file for resuming
    play_btn.config(text="⏸")  # Change button to pause

    def play():
        global is_playing
        data = wf.readframes(CHUNK)
        while data and is_playing:
            playback_stream.write(data)
            data = wf.readframes(CHUNK)

        if not is_playing:
            return  # Exit if paused

        playback_stream.stop_stream()
        playback_stream.close()
        is_playing = False  # Reset state
        status_label.config(text="Playback finished ✅", style="Blue.TLabel")
        play_btn.config(text="▶")  # Reset button to play

    threading.Thread(target=play, daemon=True).start()  # Play in a separate thread


def resume_playback():
    """Resume playback from paused position"""
    global is_playing, playback_stream, paused_data

    if paused_data:
        is_playing = True
        playback_stream = audio.open(format=audio.get_format_from_width(paused_data.getsampwidth()),
                                     channels=paused_data.getnchannels(),
                                     rate=paused_data.getframerate(),
                                     output=True)

        data = paused_data.readframes(CHUNK)
        while data and is_playing:
            playback_stream.write(data)
            data = paused_data.readframes(CHUNK)

        if not is_playing:
            return  # Exit if paused

        playback_stream.stop_stream()
        playback_stream.close()
        is_playing = False
        status_label.config(text="Playback finished ✅", style="Blue.TLabel")
        current_play_btn.config(text="▶")  # Reset button to play


# Function to stop playback
def stop_audio():
    global playback_stream, PLAYING
    PLAYING = False  # Stop playback

    if playback_stream:
        playback_stream.stop_stream()
        playback_stream.close()
        playback_stream = None


# Function to delete a recording
def delete_recording(filename):
    os.remove(f"recordings/{filename}")
    update_recordings()
    messagebox.showwarning("WARNING","This will delete the recording")
    messagebox.showinfo("Deleted", f"{filename} has been deleted.")

# GUI setup
root = tb.Window(themename="superhero")  # Modern ttkbootstrap theme
root.title("Voice Recorder")
root.geometry("400x700")

# Title label
title_label = tb.Label(root, text="🎤 Voice Recorder", font=("Arial", 18, "bold"), bootstyle="primary")
title_label.pack(pady=10)

#logo
photo=PhotoImage(file="Record.png")
myimage=Label(image=photo,background="#4a4a4a")
myimage.pack(padx=5,pady=5)

# Timer display
timer_label = tb.Label(root, text="00:00", font=("Arial", 14, "bold"), bootstyle="info")
timer_label.pack(pady=5)

# Start/Pause button
start_pause_button = tb.Button(root, text="▶ Start", command=toggle_recording, bootstyle="primary", width=12)
start_pause_button.pack(pady=5)

# Stop button
stop_button = tb.Button(root, text="⏹ Stop", command=stop_recording, bootstyle="danger", width=12)
stop_button.pack(pady=5)

# Recordings section label
recordings_label = tb.Label(root, text="Previous Recordings", font=("Arial", 12, "bold"), bootstyle="secondary", background="white")
recordings_label.pack(pady=5)

# Create a status label with the style
status_label = tb.Label(root, text="", font=("Arial", 12), anchor="w")
status_label.pack(pady=5, fill="x") 

# Scrollable Frame for Recordings
recordings_canvas = tk.Canvas(root, height=350)
recordings_scroll = ttk.Scrollbar(root, orient="vertical", command=recordings_canvas.yview)
recordings_frame = tb.Frame(recordings_canvas)
recordings_frame.pack(fill="x", expand=True)

recordings_frame.bind("<Configure>", lambda e: recordings_canvas.configure(scrollregion=recordings_canvas.bbox("all")))
recordings_window = recordings_canvas.create_window((0, 0), window=recordings_frame, anchor="nw")

recordings_canvas.configure(yscrollcommand=recordings_scroll.set)

recordings_canvas.pack(side="left", fill="both", expand=True)
recordings_scroll.pack(side="right", fill="y")

# Define style
style = tb.Style()
style.configure("Blue.TLabel", foreground="blue", font=("Arial", 12), justify="left")

# Load existing recordings
update_recordings()

# Run the GUI
root.mainloop()
audio.terminate()
