import tkinter as tk
from PIL import Image, ImageTk
import itertools

# ---- Globals ----
finished_tasks = []
focus_widgets = []
focus_flash_canvas_items = []
user_minutes = 0
current_task_name = ""
current_timer = None
checkin_canvas_items = []
checkin_widgets = []
last_timer_state = {"seconds_left": None, "checkin_points": None}

WINDOW_WIDTH, WINDOW_HEIGHT = 311, 452

root = tk.Tk()
root.title("Procrastination Station")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)

# --- UI clearing helpers ---
def clear_widget_list(lst):
    for w in lst:
        if hasattr(w, 'destroy'):
            w.destroy()
        else:
            dashboard_canvas.delete(w)
    lst.clear()

def clear_canvas_tags(*tags):
    for tag in tags:
        dashboard_canvas.delete(tag)

def clear_all_for_screen():
    clear_widget_list(focus_widgets)
    clear_widget_list(focus_flash_canvas_items)
    clear_widget_list(checkin_canvas_items)
    clear_widget_list(checkin_widgets)
    dashboard_canvas.delete("timer_text")

# --- Intro screen ---
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
canvas.pack()
bg = ImageTk.PhotoImage(Image.open("intro_bg.png").resize((WINDOW_WIDTH, WINDOW_HEIGHT)))
canvas.create_image(0, 0, anchor=tk.NW, image=bg)
chat_img = Image.open("intro_chat.png")
chat = ImageTk.PhotoImage(chat_img.resize((250, int(250 * chat_img.height / chat_img.width)), Image.Resampling.LANCZOS))
canvas.create_image((WINDOW_WIDTH - 250) // 2, -17, anchor=tk.NW, image=chat)
btn_w, btn_h, btn_y = 140, 38, 390
btn_x = (WINDOW_WIDTH - btn_w) // 2
shadow = canvas.create_rectangle(btn_x + 3, btn_y + 3, btn_x + btn_w + 3, btn_y + btn_h + 3, fill="#cccc99", outline="")
button = canvas.create_rectangle(btn_x, btn_y, btn_x + btn_w, btn_y + btn_h, fill="#FFE066", outline="#FFA500", width=5)
btn_text = canvas.create_text(btn_x + btn_w // 2, btn_y + btn_h // 2, text="Let's do this!", font=("Arial", 18, "bold"), fill="#000")

# --- Dashboard assets ---
dashboard_canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
main_bg = ImageTk.PhotoImage(Image.open("MAIN_BK.png").resize((WINDOW_WIDTH, WINDOW_HEIGHT)))
speech_img = tk.PhotoImage(file="SPEECH_1.png")
nudge_img = tk.PhotoImage(file="NUDGE_1.png")
nudgespeech2_img = tk.PhotoImage(file="NUDGESPEECH_2.png")

# --- Timer/Check-in/Break/Celebration logic ---
def show_timer_screen(minutes, checkin_count):
    clear_all_for_screen()
    dashboard_canvas.create_image(0, 0, image=main_bg, anchor="nw")
    timer_img = tk.PhotoImage(file="timer.png")
    dashboard_canvas.create_image(0, 0, image=timer_img, anchor="nw")
    dashboard_canvas.timer_img = timer_img
    total_seconds = int(minutes) * 60
    if checkin_count > 1:
        interval = total_seconds // checkin_count
        checkin_times = [total_seconds - interval * i for i in range(1, checkin_count)] + [0]
    else:
        checkin_times = [0]
    run_timer(total_seconds, checkin_times)

def run_timer(seconds_left, checkin_points):
    dashboard_canvas.delete("timer_text")
    clear_widget_list(checkin_canvas_items)
    clear_widget_list(checkin_widgets)
    time_str = f"{seconds_left//60:02d}:{seconds_left%60:02d}"
    dashboard_canvas.create_text(156, 215, text=time_str, font=("Arial", 65, "bold"), fill="#191919", tags="timer_text")
    if not (checkin_points and seconds_left == checkin_points[0]) and seconds_left > 0:
        finished_btn = tk.Button(
            root, text="Finished Task", font=("Arial", 10, "bold"),
            width=14, height=1, bg="#fdf9ce", fg="#995c25", relief="solid", bd=2,
            highlightbackground="#a75b14", highlightthickness=2,
            command=show_celebration_screen, cursor="hand2"
        )
        dashboard_canvas.create_window(156, 295, window=finished_btn, width=120, height=32)
        checkin_widgets.append(finished_btn)
    if checkin_points and seconds_left == checkin_points[0]:
        last_timer_state["seconds_left"] = seconds_left
        last_timer_state["checkin_points"] = checkin_points[1:]
        show_canvas_checkin(seconds_left, checkin_points)
        return
    if seconds_left > 0:
        global current_timer
        current_timer = root.after(1000, lambda: run_timer(seconds_left - 1, checkin_points))
    else:
        dashboard_canvas.delete("timer_text")
        dashboard_canvas.create_text(156, 226, text="Time's up!", font=("Arial", 28, "bold"), fill="#a75b14")
        finished_btn = tk.Button(
            root, text="Finished Task", font=("Arial", 10, "bold"),
            width=14, height=1, bg="#fdf9ce", fg="#995c25", relief="solid", bd=2,
            highlightbackground="#a75b14", highlightthickness=2,
            command=show_celebration_screen, cursor="hand2"
        )
        dashboard_canvas.create_window(156, 295, window=finished_btn, width=120, height=32)
        checkin_widgets.append(finished_btn)

def show_canvas_checkin(seconds_left, checkin_points):
    dashboard_canvas.delete("timer_text")
    nudge_checkin_img = tk.PhotoImage(file="NUDGE_checkin.png")
    img_id = dashboard_canvas.create_image(0, 0, image=nudge_checkin_img, anchor="nw")
    dashboard_canvas.nudge_checkin_img = nudge_checkin_img
    checkin_canvas_items.append(img_id)
    btn_w, btn_h = 140, 36
    x, y_top, y_gap = 90, 240, 58
    def on_keep_going():
        clear_widget_list(checkin_canvas_items)
        clear_widget_list(checkin_widgets)
        if seconds_left == 0:
            show_celebration_screen()
        else:
            run_timer(seconds_left - 1, checkin_points[1:])
    def on_distracted():
        clear_widget_list(checkin_canvas_items)
        clear_widget_list(checkin_widgets)
        show_distracted_screen()
    keep_going_btn = tk.Button(root, text="You know it!", font=("Arial", 13, "bold"),
                              bg="#74d47b", fg="black", activebackground="#57bb5a", activeforeground="black",
                              width=15, height=1, relief="solid", bd=2,
                              highlightbackground="#74d47b", highlightthickness=2,
                              cursor="hand2", command=on_keep_going)
    dashboard_canvas.create_window(x, y_top, window=keep_going_btn, width=btn_w, height=btn_h)
    checkin_widgets.append(keep_going_btn)
    distracted_btn = tk.Button(root, text="Not really...", font=("Arial", 13, "bold"),
                               bg="#e95a5a", fg="black", activebackground="#b62b2b", activeforeground="black",
                               width=15, height=1, relief="solid", bd=2,
                               highlightbackground="#e95a5a", highlightthickness=2,
                               cursor="hand2", command=on_distracted)
    dashboard_canvas.create_window(x, y_top + y_gap, window=distracted_btn, width=btn_w, height=btn_h)
    checkin_widgets.append(distracted_btn)

def show_distracted_screen():
    dashboard_canvas.delete("timer_text")
    clear_widget_list(checkin_canvas_items)
    clear_widget_list(checkin_widgets)
    dashboard_canvas.create_image(0, 0, image=main_bg, anchor="nw")
    distracted_img = tk.PhotoImage(file="NUDGEdistracted.png")
    dashboard_canvas.distracted_img = distracted_img
    distracted_id = dashboard_canvas.create_image(0, 0, image=distracted_img, anchor="nw")
    checkin_canvas_items.append(distracted_id)
    btn_w, btn_h = 100, 30
    x_left, y_start, y_gap = 30, 160, 35
    def keep_going():
        clear_widget_list(checkin_canvas_items)
        clear_widget_list(checkin_widgets)
        run_timer(last_timer_state["seconds_left"], last_timer_state["checkin_points"])
    def take_a_break():
        clear_widget_list(checkin_canvas_items)
        clear_widget_list(checkin_widgets)
        show_break_timer()
    def restart_timer():
        clear_widget_list(checkin_canvas_items)
        clear_widget_list(checkin_widgets)
        show_time_entry_screen()
    def restart_task():
        clear_widget_list(checkin_canvas_items)
        clear_widget_list(checkin_widgets)
        show_dashboard()
    btns = [
        ("Keep going", keep_going),
        ("Take a break", take_a_break),
        ("Restart timer", restart_timer),
        ("Restart task", restart_task),
    ]
    for i, (label, cmd) in enumerate(btns):
        btn = tk.Button(
            root, text=label, font=("Arial", 11, "bold"),
            width=13, height=1, bg="#fffbe3", fg="#191919", relief="solid", bd=2,
            highlightbackground="#c97a11", highlightcolor="#c97a11", highlightthickness=2,
            command=cmd, cursor="hand2"
        )
        dashboard_canvas.create_window(x_left, y_start + i*y_gap, window=btn, width=btn_w, height=btn_h, anchor="nw")
        checkin_widgets.append(btn)

def show_break_timer():
    clear_widget_list(checkin_canvas_items)
    clear_widget_list(checkin_widgets)
    dashboard_canvas.delete("timer_text")
    break_seconds = 5 * 60
    def update_break_timer(secs_left):
        dashboard_canvas.delete("timer_text")
        time_str = f"{secs_left//60:02d}:{secs_left%60:02d}"
        dashboard_canvas.create_text(156, 190, text=time_str, font=("Arial", 65, "bold"), fill="#191919", tags="timer_text")
        if secs_left > 0:
            root.after(1000, lambda: update_break_timer(secs_left - 1))
        else:
            back_btn = tk.Button(
                root, text="Back to task", font=("Arial", 14, "bold"),
                width=15, height=1, bg="#fdf9ce", fg="#191919", relief="solid", bd=2,
                highlightbackground="#c97a11", highlightthickness=2,
                command=lambda: run_timer(last_timer_state["seconds_left"], last_timer_state["checkin_points"]),
                cursor="hand2"
            )
            dashboard_canvas.create_window(156, 265, window=back_btn, width=145, height=40)
            checkin_widgets.append(back_btn)
    update_break_timer(break_seconds)

def show_celebration_screen():
    global finished_tasks, current_task_name, current_timer
    if current_task_name and current_task_name not in finished_tasks:
        finished_tasks.append(current_task_name)
    current_task_name = ""
    if current_timer is not None:
        root.after_cancel(current_timer)
        current_timer = None
    clear_all_for_screen()
    for item in dashboard_canvas.find_all():
        if dashboard_canvas.type(item) == "image":
            img_obj = dashboard_canvas.itemcget(item, 'image')
            if img_obj != str(main_bg):
                dashboard_canvas.delete(item)
        elif dashboard_canvas.type(item) in ("text", "rectangle", "window"):
            dashboard_canvas.delete(item)
    rainbow_colors = ["#FF5E5B", "#FFB84C", "#F9FF5B", "#4CFFB8", "#4CA6FF", "#B04CFF", "#FF4CF2"]
    rects = []
    height = WINDOW_HEIGHT // len(rainbow_colors)
    for i, color in enumerate(rainbow_colors):
        rect = dashboard_canvas.create_rectangle(0, i*height, WINDOW_WIDTH, (i+1)*height, fill=color, outline="")
        rects.append(rect)
    def animate_rainbow():
        rainbow_colors.append(rainbow_colors.pop(0))
        for i, rect in enumerate(rects):
            dashboard_canvas.itemconfig(rect, fill=rainbow_colors[i])
        dashboard_canvas.after(150, animate_rainbow)
    animate_rainbow()
    celebration_img = tk.PhotoImage(file="NUDGEcelebration.png")
    dashboard_canvas.celebration_img = celebration_img
    image_id = dashboard_canvas.create_image(0, 0, image=celebration_img, anchor="nw")
    celebration_text_img = tk.PhotoImage(file="celebration_text.png")
    dashboard_canvas.celebration_text_img = celebration_text_img
    text_id = dashboard_canvas.create_image(0, 0, image=celebration_text_img, anchor="nw")
    from PIL import Image as PilImage, ImageTk as PilImageTk
    pil_img = PilImage.open("NUDGEcelebration.png")
    pil_img_flip = pil_img.transpose(PilImage.FLIP_LEFT_RIGHT)
    celebration_img_flip = PilImageTk.PhotoImage(pil_img_flip)
    dashboard_canvas.celebration_img_flip = celebration_img_flip
    def flip():
        current = dashboard_canvas.itemcget(image_id, 'image')
        dashboard_canvas.itemconfig(image_id, image=celebration_img_flip if current == str(celebration_img) else celebration_img)
        dashboard_canvas.after(500, flip)
    flip()
    def next_task():
        clear_widget_list(checkin_widgets)
        for item in rects:
            dashboard_canvas.delete(item)
        dashboard_canvas.delete(image_id)
        dashboard_canvas.delete(text_id)
        for item in dashboard_canvas.find_all():
            if dashboard_canvas.type(item) != "image" or dashboard_canvas.itemcget(item, 'image') != str(main_bg):
                dashboard_canvas.delete(item)
        show_dashboard()
    next_btn = tk.Button(
        root, text="Next task!", font=("Arial", 15, "bold"),
        width=15, height=1, bg="#fffbe3", fg="#995c25", relief="solid", bd=2,
        highlightbackground="#a75b14", highlightthickness=2,
        command=next_task, cursor="hand2"
    )
    dashboard_canvas.create_window(156, 350, window=next_btn, width=160, height=40)
    checkin_widgets.append(next_btn)

def show_focus_flash(png_path, message, minutes, checkin_count):
    clear_all_for_screen()
    dashboard_canvas.delete("nudgespeech3")
    dashboard_canvas.delete("prompt3")
    img = tk.PhotoImage(file=png_path)
    img_id = dashboard_canvas.create_image(0, 0, image=img, anchor="nw")
    dashboard_canvas.nudge_flash_img = img
    text_id = dashboard_canvas.create_text(156, 90, text=message, font=("Courier", 14, "bold"), fill="#2b2b2b", width=240, anchor="center")
    focus_flash_canvas_items.clear()
    focus_flash_canvas_items.extend([img_id, text_id])
    root.after(5000, lambda: show_timer_screen(minutes, checkin_count))

def show_focus_screen():
    clear_canvas_tags("nudgespeech2", "time_entry", "border2", "minutes_label", "prompt2")
    clear_widget_list(focus_flash_canvas_items)
    clear_widget_list(focus_widgets)
    clear_widget_list(checkin_canvas_items)
    clear_widget_list(checkin_widgets)
    nudgespeech3_img = tk.PhotoImage(file="NUDGESPEECH_3.png")
    dashboard_canvas.create_image(0, 0, image=nudgespeech3_img, anchor="nw", tags="nudgespeech3")
    dashboard_canvas.nudgespeech3_img = nudgespeech3_img
    dashboard_canvas.create_text(156, 90, text="...aaand how focused are you feeling?", font=("Courier", 14, "bold"),
                                fill="#2b2b2b", tags="prompt3", width=240, anchor="center")
    window_width, button_width, button_height = 311, 100, 25
    button_gap_x, button_gap_y, top_y = 16, 5, 272
    total_width = button_width * 2 + button_gap_x
    left_edge = (window_width - total_width) // 2
    positions = [
        (left_edge, top_y),
        (left_edge + button_width + button_gap_x, top_y),
        (left_edge, top_y + button_height + button_gap_y),
        (left_edge + button_width + button_gap_x, top_y + button_height + button_gap_y),
    ]
    labels = [
        ("SUPER focused", "NUDGESPEECH_3_1.png", "Oh wow! So I wont check in if you're still on task. Superstar!!", 1),
        ("Pretty locked in", "NUDGESPEECH_3_2.png", "ooohh yeah! I'll check in on you twice to make sure you're still on track.", 2),
        ("Need some help", "NUDGESPEECH_3_3.png", "No worries! I'll say hi 3 times to check in. You got this!", 3),
        ("NOT AT ALL!!", "NUDGESPEECH_3_4.png", "That's okay! Take a breath. I'll come back 4 times to check in.", 4),
    ]
    for (label, png, msg, checkin_count), (x, y) in zip(labels, positions):
        btn = tk.Button(
            root, text=label, font=("Arial", 9, "bold"),
            width=14, height=1, bg="#fdf9ce", fg="#a75b14", relief="solid", bd=2,
            highlightthickness=0, highlightbackground="#c97a11",
            activebackground="#FFE066", activeforeground="#a75b14",
            cursor="hand2", command=lambda p=png, m=msg, c=checkin_count: show_focus_flash(p, m, user_minutes, c)
        )
        btn.configure(bg="#fdf9ce")
        dashboard_canvas.create_window(x + button_width // 2, y + button_height // 2, window=btn, width=button_width, height=button_height)
        focus_widgets.append(btn)

def show_time_entry_screen():
    clear_widget_list(checkin_canvas_items)
    clear_widget_list(checkin_widgets)
    dashboard_canvas.delete("timer_text")
    nudgespeech2_img = tk.PhotoImage(file="NUDGESPEECH_2.png")
    dashboard_canvas.create_image(0, 0, image=nudgespeech2_img, anchor="nw", tags="nudgespeech2")
    dashboard_canvas.nudgespeech2_img = nudgespeech2_img
    dashboard_canvas.create_text(156, 90, text="Great! How long will your task take?", font=("Courier", 14, "bold"),
                                fill="#2b2b2b", tags="prompt2", anchor="center", width=220)
    MIN_BOX_WIDTH, MIN_BOX_HEIGHT, MIN_BOX_X, MIN_BOX_Y = 60, 25, 126, 300
    BORDER_COLOR = "#c97a11"
    dashboard_canvas.create_rectangle(
        MIN_BOX_X - MIN_BOX_WIDTH // 2 - 1, MIN_BOX_Y - MIN_BOX_HEIGHT // 2 - 1,
        MIN_BOX_X + MIN_BOX_WIDTH // 2 + 1, MIN_BOX_Y + MIN_BOX_HEIGHT // 2 + 1,
        outline=BORDER_COLOR, width=2, fill="#fdf9ce", tags="border2"
    )
    time_entry = tk.Entry(root, font=("Arial", 12, "bold"), justify="center", fg="#888888", bg="#fffbe3",
                         borderwidth=0, highlightthickness=0)
    time_entry.insert(0, "Minutes")
    dashboard_canvas.create_window(MIN_BOX_X, MIN_BOX_Y, window=time_entry, width=MIN_BOX_WIDTH,
                                  height=MIN_BOX_HEIGHT, tags="time_entry")
    time_entry.focus()
    def on_time_entry_click(event):
        if event.widget.get() == "Minutes":
            event.widget.delete(0, tk.END)
            event.widget.config(fg="#333333")
    def on_time_focusout(event):
        if event.widget.get() == "":
            event.widget.insert(0, "Minutes")
            event.widget.config(fg="#888888")
    def on_time_entry_return(event):
        global user_minutes
        time_val = event.widget.get().strip()
        if not time_val.isdigit():
            return
        user_minutes = int(time_val)
        show_focus_screen()
    time_entry.bind('<FocusIn>', on_time_entry_click)
    time_entry.bind('<FocusOut>', on_time_focusout)
    time_entry.bind('<Return>', on_time_entry_return)
    dashboard_canvas.create_text(MIN_BOX_X + MIN_BOX_WIDTH // 2 + 10, MIN_BOX_Y,
                                text="minutes", font=("Arial", 12, "bold"),
                                fill="#995c25", anchor="w", tags="minutes_label")

def show_dashboard():
    canvas.pack_forget()
    dashboard_canvas.pack()
    dashboard_canvas.create_image(0, 0, anchor=tk.NW, image=main_bg)
    project_name_entry = tk.Entry(root, font=("Comic Sans MS", 20, "bold"), justify="center", fg="#FFFFFF",
                                  bg="#FFCD62", borderwidth=0, highlightthickness=0)
    project_name_entry.insert(0, "*PROJECT NAME*")
    dashboard_canvas.create_window(WINDOW_WIDTH // 2, 28, window=project_name_entry, width=260, height=25)
    finished_label = tk.Label(root, text="Finished tasks", font=("Arial", 13, "bold", "underline"),
                              fg="#995c25", bg="#ffe58a", anchor="w")
    dashboard_canvas.create_window(35, 325, window=finished_label, anchor="nw")
    left_tasks = finished_tasks[:3]
    right_tasks = finished_tasks[3:6]
    tasks_left = "\n".join(f"• {t}" for t in left_tasks) if left_tasks else ""
    left_label = tk.Label(root, text=tasks_left, font=("Arial", 12), fg="#995c25", bg="#ffe58a", justify="left")
    dashboard_canvas.create_window(35, 345, window=left_label, anchor="nw")
    tasks_right = "\n".join(f"• {t}" for t in right_tasks) if right_tasks else ""
    right_label = tk.Label(root, text=tasks_right, font=("Arial", 12), fg="#995c25", bg="#ffe58a", justify="left")
    dashboard_canvas.create_window(170, 345, window=right_label, anchor="nw")
    dashboard_canvas.create_image(0, 22, image=speech_img, anchor="nw", tags="speech1")
    dashboard_canvas.create_image(0, 0, image=nudge_img, anchor="nw", tags="nudge1")
    BOX_WIDTH, BOX_HEIGHT, BOX_X, BOX_Y = 150, 25, 156, 300
    BORDER_COLOR = "#c97a11"
    dashboard_canvas.create_rectangle(
        BOX_X - BOX_WIDTH // 2 - 1, BOX_Y - BOX_HEIGHT // 2 - 1,
        BOX_X + BOX_WIDTH // 2 + 1, BOX_Y + BOX_HEIGHT // 2 + 1,
        outline=BORDER_COLOR, width=2, fill="#fdf9ce", tags="border1"
    )
    def on_task_entry_click(event):
        if event.widget.get() == "Type your task here...":
            event.widget.delete(0, tk.END)
            event.widget.config(fg="#333333")
    def on_task_focusout(event):
        if event.widget.get() == "":
            event.widget.insert(0, "Type your task here...")
            event.widget.config(fg="#888888")
    def on_task_entry_return(event):
        global current_task_name
        task = task_entry.get().strip()
        if not task or task == "Type your task here...":
            return
        current_task_name = task
        dashboard_canvas.delete("nudge1")
        dashboard_canvas.delete("speech1")
        dashboard_canvas.delete("task_entry")
        dashboard_canvas.delete("border1")
        dashboard_canvas.create_image(0, 0, image=nudgespeech2_img, anchor="nw", tags="nudgespeech2")
        dashboard_canvas.create_text(156, 90, text=f"Great! How long will {task} take?", font=("Courier", 14, "bold"),
                                    fill="#2b2b2b", tags="prompt2", anchor="center", width=220)
        MIN_BOX_WIDTH, MIN_BOX_HEIGHT, MIN_BOX_X, MIN_BOX_Y = 60, 25, 126, 300
        dashboard_canvas.create_rectangle(
            MIN_BOX_X - MIN_BOX_WIDTH // 2 - 1, MIN_BOX_Y - MIN_BOX_HEIGHT // 2 - 1,
            MIN_BOX_X + MIN_BOX_WIDTH // 2 + 1, MIN_BOX_Y + MIN_BOX_HEIGHT // 2 + 1,
            outline=BORDER_COLOR, width=2, fill="#fdf9ce", tags="border2"
        )
        time_entry = tk.Entry(root, font=("Arial", 12, "bold"), justify="center", fg="#888888", bg="#fffbe3",
                             borderwidth=0, highlightthickness=0)
        time_entry.insert(0, "Minutes")
        dashboard_canvas.create_window(MIN_BOX_X, MIN_BOX_Y, window=time_entry, width=MIN_BOX_WIDTH,
                                      height=MIN_BOX_HEIGHT, tags="time_entry")
        time_entry.focus()
        def on_time_entry_click(event):
            if event.widget.get() == "Minutes":
                event.widget.delete(0, tk.END)
                event.widget.config(fg="#333333")
        def on_time_focusout(event):
            if event.widget.get() == "":
                event.widget.insert(0, "Minutes")
                event.widget.config(fg="#888888")
        def on_time_entry_return(event):
            global user_minutes
            time_val = event.widget.get().strip()
            if not time_val.isdigit():
                return
            user_minutes = int(time_val)
            show_focus_screen()
        time_entry.bind('<FocusIn>', on_time_entry_click)
        time_entry.bind('<FocusOut>', on_time_focusout)
        time_entry.bind('<Return>', on_time_entry_return)
        dashboard_canvas.create_text(MIN_BOX_X + MIN_BOX_WIDTH // 2 + 10, MIN_BOX_Y,
                                    text="minutes", font=("Arial", 12, "bold"),
                                    fill="#995c25", anchor="w", tags="minutes_label")
    task_entry = tk.Entry(root, font=("Arial", 12, "bold"), justify="center", fg="#888888", bg="#fffbe3",
                         borderwidth=0, highlightthickness=0)
    task_entry.insert(0, "Type your task here...")
    task_entry.bind('<FocusIn>', on_task_entry_click)
    task_entry.bind('<FocusOut>', on_task_focusout)
    task_entry.bind('<Return>', on_task_entry_return)
    dashboard_canvas.create_window(BOX_X, BOX_Y, window=task_entry, width=BOX_WIDTH, height=BOX_HEIGHT, tags="task_entry")
    task_entry.focus()

def on_press(e):
    canvas.itemconfig(button, fill="#FFD54F")
    canvas.coords(shadow, btn_x + 1, btn_y + 1, btn_x + btn_w + 1, btn_y + btn_h + 1)
def on_release(e):
    canvas.itemconfig(button, fill="#FFE066")
    canvas.coords(shadow, btn_x + 3, btn_y + 3, btn_x + btn_w + 3, btn_y + btn_h + 3)
    show_dashboard()
for item in (button, btn_text):
    canvas.tag_bind(item, "<ButtonPress-1>", on_press)
    canvas.tag_bind(item, "<ButtonRelease-1>", on_release)

root.mainloop()