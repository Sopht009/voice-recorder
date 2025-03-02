import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter import *
import pyaudio
import wave
import os
import sounddevice as sa
import threading

# Global variables
recording = False
frames = []
output_filename = "recording.wav"
sample_rate = 44100
channels = 2
format = pyaudio.paInt16

def start_recording():
    global recording, frames
    recording = True
    frames = []
    thread = threading.Thread(target=record_audio)
    thread.start()
    status_label.config(text="Recording...", fg="red")

def stop_recording():
    global recording
    recording = False
    status_label.config(text="Recording Stopped", fg="black")

def record_audio():
    global frames
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=1024)
    
    while recording:
        data = stream.read(1024)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    save_audio()

def save_audio():
    global frames
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if not file_path:
        return
    
    audio = pyaudio.PyAudio()
    wave_file = wave.open(file_path, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(audio.get_sample_size(format))
    wave_file.setframerate(sample_rate)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    
    status_label.config(text=f"Saved: {file_path}", fg="green")
    refresh_recordings()

def play_audio():
    selected = recordings_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Select a file to play")
        return
    
    file_path = recordings_listbox.get(selected[0])
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def refresh_recordings():
    recordings_listbox.delete(0, tk.END)
    files = [f for f in os.listdir() if f.endswith(".wav")]
    for f in files:
        recordings_listbox.insert(tk.END, f)

def delete_recording():
    selected = recordings_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Select a file to delete")
        return
    file_path = recordings_listbox.get(selected[0])
    os.remove(file_path)
    refresh_recordings()

def rename_recording():
    selected = recordings_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Select a file to rename")
        return
    old_name = recordings_listbox.get(selected[0])
    new_name = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if new_name:
        os.rename(old_name, new_name)
        refresh_recordings()

# GUI Setup
root = tk.Tk()
root.title("Voice Recorder")
root.geometry("400x400")
root.configure(bg="#222")

#icon
image_icon=PhotoImage(file="Record.png")
root.iconphoto(False,image_icon)

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=5)

status_label = tk.Label(root, text="Click Start to Record", fg="white", bg="#222", font=("Arial", 12))
status_label.pack(pady=10)

start_button = ttk.Button(root, text="Start Recording", command=start_recording)
start_button.pack(pady=5)
image_icon=PhotoImage(file="voice_button.png")
start_button.iconphoto(False,image_icon)

stop_button = ttk.Button(root, text="Stop Recording", command=stop_recording)
stop_button.pack(pady=5)

play_button = ttk.Button(root, text="Play", command=play_audio)
play_button.pack(pady=5)

save_button = ttk.Button(root, text="Save", command=save_audio)
save_button.pack(pady=5)

delete_button = ttk.Button(root, text="Delete", command=delete_recording)
delete_button.pack(pady=5)

rename_button = ttk.Button(root, text="Rename", command=rename_recording)
rename_button.pack(pady=5)

recordings_listbox = tk.Listbox(root, width=40, height=8)
recordings_listbox.pack(pady=10)
refresh_recordings()

# Scrollable Frame for Recordings
recordings_canvas = tk.Canvas(root, height=350)
recordings_scroll = ttk.Scrollbar(root, orient="vertical", command=recordings_canvas.yview)
recordings_frame = tk.Frame(recordings_canvas)
recordings_frame.pack(fill="x", expand=True)

recordings_frame.bind("<Configure>", lambda e: recordings_canvas.configure(scrollregion=recordings_canvas.bbox("all")))
recordings_window = recordings_canvas.create_window((0, 0), window=recordings_frame, anchor="nw")

recordings_canvas.configure(yscrollcommand=recordings_scroll.set)

recordings_canvas.pack(side="left", fill="both", expand=True)
recordings_scroll.pack(side="right", fill="y")

root.mainloop()
