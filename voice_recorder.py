import tkinter as tk

root = tk.Tk()

# Load image
photo = tk.PhotoImage(file="Record.png")  # Only supports PNG and GIF

# Create button with image
button = tk.Button(root, text="Click Me", image=photo)

button.pack()

root.mainloop()
photo=PhotoImage(file="Record.png")
myimage=Label(image=photo,background="#4a4a4a")
myimage.pack(padx=5,pady=5)
