import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.geometry("500x300")

bg_img = Image.open("intro_bg.png")
bg_photo = ImageTk.PhotoImage(bg_img)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

chat_img = Image.open("intro_chat.png")
chat_photo = ImageTk.PhotoImage(chat_img)
chat_label = tk.Label(root, image=chat_photo, borderwidth=0, highlightthickness=0)
chat_label.place(x=50, y=30)

root.mainloop()
