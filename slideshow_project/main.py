from collections import deque
import platform
import random
from threading import Thread, Lock
from tkinter import Tk, Label, constants as TkinterConstants, PhotoImage
from PIL import Image, ImageTk, ImageGrab, ImageOps
import settings, helper

# Constants
BUFFER_SIZE = 5

# Variables
photo_dir_path: str
img_file_names: list
next_img_deque: deque
prev_img_deque: deque
forward_buffer_index: int
backward_buffer_index: int = -1

app_settings: settings.SlideSettings
screen_size: None # tuple(int, int)
current_img = None
current_tk_photo = None #tkinter requires a reference to the Tk Image or it wont be shown

# Slide State
isPaused = False
isFullscreen: bool = True

# Thread Locks used for preloading images on diff threads
next_img_deque_lock = Lock()
prev_img_deque_lock = Lock()

# ***************************************
# KEY BINDS
# ***************************************

def exit_slideshow(event=None):
    stop_slideshow()
    if "remove_speed_text_task_id" in globals():
        speed_change_label.after_cancel(remove_speed_text_task_id)
    tk_window.destroy()

def fullscreen(event=None):
	global isFullscreen
	tk_window.attributes('-fullscreen', not isFullscreen)
	isFullscreen = not isFullscreen

def pause_slideshow(event=None):
    global isPaused, schedule_next_photo_task_id
    if isPaused:
        isPaused = False
        pause_label.place_forget()
        schedule_next_photo_task_id = tk_window.after(app_settings.delay_ms, schedule_next_photo)

        photo_file_name_label.place_forget()
    else:
        stop_slideshow()
        pause_label.place(relx=0.5, y=10, anchor="n")
        isPaused = True

        photo_file_name_label.config(text=current_img.file_name)
        photo_file_name_label.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

def speedup_slideshow(event=None):
    if(app_settings.delay_ms > settings.MIN_DELAY_MS):
        app_settings.delay_ms = app_settings.delay_ms - 500
        update_settings_label()
        display_speed(app_settings.delay_ms)

def slowdown_slideshow(event=None):
    if(app_settings.delay_ms  < settings.MAX_DELAY_MS):
        app_settings.delay_ms  = app_settings.delay_ms + 500
        update_settings_label()
        display_speed(app_settings.delay_ms)

def show_settings(event=None):
    if slide_settings_label.winfo_ismapped():
        slide_settings_label.place_forget()
    else:
        update_settings_label()
        slide_settings_label.place(relx=0.0, rely=1.0, x=10, y=-10, anchor="sw")

def display_speed(speed_ms):
    global remove_speed_text_task_id
    if "remove_speed_text_task_id" in globals():
        speed_change_label.after_cancel(remove_speed_text_task_id)
    speed_change_label.config(text=helper.ms_to_sec(speed_ms) + " seconds")
    if not speed_change_label.winfo_ismapped():
        speed_change_label.place(relx=0.5, rely=1.0, y=-50, anchor="s")
    remove_speed_text_task_id = speed_change_label.after(1000, speed_change_label.place_forget)

def next_photo(event=None):
    global current_img, current_tk_photo, backward_buffer_index

    # Check if deque is not empty
    if next_img_deque:
        temp_img = current_img

        current_img = next_img_deque.popleft()
        current_tk_photo = ImageTk.PhotoImage(current_img)

        tk_photo_label.config(image=current_tk_photo)
        update_labels()

        if temp_img:
            with prev_img_deque_lock:
                if (len(prev_img_deque) == prev_img_deque.maxlen):
                    prev_img_deque.popleft().close()
                    backward_buffer_index = backward_buffer_index + 1
                prev_img_deque.append(temp_img)
        
        # Call method on a different thread to open a new image and append it to next_img_deque (parallelism)
        Thread(target=preload_next_image, daemon=True).start()
          
def previous_photo(event=None):
    global current_img, current_tk_photo, forward_buffer_index

    # Check if deque is not empty
    if prev_img_deque:
        temp_img = current_img

        current_img = prev_img_deque.pop()
        current_tk_photo = ImageTk.PhotoImage(current_img)
        update_labels()

        tk_photo_label.config(image=current_tk_photo)

        if temp_img:
            with next_img_deque_lock:
                if (len(next_img_deque) == next_img_deque.maxlen):
                    next_img_deque.pop().close()
                    forward_buffer_index = forward_buffer_index - 1

                next_img_deque.appendleft(temp_img)

        Thread(target=preload_previous_image, daemon=True).start()

def print_info(event=None):
    print("***************")
    print("***************")
    print()
    print("img_file_names size:", len(img_file_names))
    print("img_file_names:", img_file_names)
    print()
    print("frwd_buf_index:", forward_buffer_index)
    print("bkwrd_buf_index:", backward_buffer_index)
    print()
    print("prev_q", len(prev_img_deque), [obj.file_name for obj in prev_img_deque])
    print("curr_img:", current_img.file_name)
    print("next_q", len(next_img_deque), [obj.file_name for obj in next_img_deque])
    print()
    print("***************")
    print("***************")

# ***************************************
# Functions that run in background thread
# ***************************************
def preload_next_image():
    global forward_buffer_index, backward_buffer_index
    try:
        with next_img_deque_lock:

            # Reset Indexes when reaching the end of photo set
            if forward_buffer_index >= len(img_file_names):
                forward_buffer_index = 0
                with prev_img_deque_lock:
                    backward_buffer_index = -(BUFFER_SIZE*2+1) # this is to account for photos already in prev buffer deque
                if app_settings.isRandomized:
                     random.shuffle(img_file_names)

            img = Image.open(fp = photo_dir_path + img_file_names[forward_buffer_index], formats=settings.VALID_FORMATS)

            if False if img.getexif().get(0x0112) == 1 else True:
                img = ImageOps.exif_transpose(img)
            if app_settings.isCropped:
                img = ImageOps.fit(image=img, size=screen_size, method=Image.Resampling.LANCZOS)
            else:
                img = ImageOps.contain(image=img, size=screen_size, method=Image.Resampling.LANCZOS)
            img.file_name = img_file_names[forward_buffer_index]
            img.index = forward_buffer_index

            # Add Next Photo
            next_img_deque.append(img)
            forward_buffer_index = forward_buffer_index + 1
    except Exception as e:
        print(f"Error Loading Next Photo: {e}")

def preload_previous_image():
    global backward_buffer_index
    try:
        with prev_img_deque_lock:
            if (backward_buffer_index > -1):
                img = Image.open(fp = photo_dir_path + img_file_names[backward_buffer_index], formats=settings.VALID_FORMATS)

                if False if img.getexif().get(0x0112) == 1 else True:
                    img = ImageOps.exif_transpose(img)
                if app_settings.isCropped:
                    img = ImageOps.fit(image=img, size=screen_size, method=Image.Resampling.LANCZOS)
                else:
                    img = ImageOps.contain(image=img, size=screen_size, method=Image.Resampling.LANCZOS)
                img.file_name = img_file_names[backward_buffer_index]
                img.index = backward_buffer_index

                # Add Previous Photo
                prev_img_deque.appendleft(img)
                backward_buffer_index = backward_buffer_index - 1
    except Exception as e:
        print(f"Error Loading Previous Photo: {e}")

# ***************************************

def stop_slideshow():
    tk_window.after_cancel(schedule_next_photo_task_id)

def update_labels():
    photo_count_label.config(text=f"{current_img.index + 1} / {len(img_file_names)}")
    photo_file_name_label.config(text=current_img.file_name)

def update_settings_label():
    slide_settings_label.config(text=str(app_settings))

def schedule_next_photo():
    global schedule_next_photo_task_id, current_img, current_tk_photo, backward_buffer_index

    # Check if photos avaiable
    if next_img_deque:
        temp_img = current_img

        current_img = next_img_deque.popleft()
        current_tk_photo = ImageTk.PhotoImage(current_img)

        tk_photo_label.config(image=current_tk_photo)
        update_labels()

        if temp_img:
            with prev_img_deque_lock:
                if (len(prev_img_deque) == prev_img_deque.maxlen):
                    prev_img_deque.popleft().close()
                    backward_buffer_index = backward_buffer_index + 1
                prev_img_deque.append(temp_img)
        
        # Call method on a different thread to open a new image and append it to next_img_deque (parallelism)
        Thread(target=preload_next_image, daemon=True).start()

        schedule_next_photo_task_id = tk_window.after(app_settings.delay_ms, schedule_next_photo)
    else:
        # If next photo deque is empty, the background thread is still loading photos. So we want to schedule another photo or the slide will stop
        tk_window.after_cancel(schedule_next_photo_task_id)
        schedule_next_photo_task_id = tk_window.after(app_settings.delay_ms, schedule_next_photo)

def load_initial_photos():
    global forward_buffer_index
    print("\n Attempting To Load Initial Photos")
    for index, file_name in enumerate(img_file_names):
        try:

            forward_buffer_index = index
            if(len(next_img_deque) == next_img_deque.maxlen):
                break

            img = Image.open(fp = photo_dir_path + file_name, formats=settings.VALID_FORMATS)

            # Checks if the orientation tag present isn't 1 (no tranpose needed)
            # I found checking for orientation tag saves a couple seconds rather than applying exif_transpose on all images and returning a copy
            isTransposed = False if img.getexif().get(0x0112) == 1 else True # 2-8 means the image has a orientation tag that programs apply when viewing
            if isTransposed:
                img = ImageOps.exif_transpose(img) #  applies orientation transpose

            if app_settings.isCropped:
                img = ImageOps.fit(image=img, size=screen_size, method=Image.Resampling.LANCZOS)
            else:
                img = ImageOps.contain(image=img, size=screen_size, method=Image.Resampling.LANCZOS)

            img.file_name = file_name
            img.index = index
            next_img_deque.append(img)
            print(" +[LOADED] -", file_name, ("(photo transposed)" if isTransposed else '') )

        except Exception as e:
            print(" -[FAILED] -", e)

# ---- Run Everything ----
if __name__ == "__main__":
    helper.print_controls(settings.MIN_DELAY_MS, settings.MAX_DELAY_MS)

    # Initialize deque and set the max length
    next_img_deque = deque(maxlen=BUFFER_SIZE)
    prev_img_deque = deque(maxlen=BUFFER_SIZE)

    # Grab slideshow settings from cmd line options and or user input
    app_settings = settings.get_cmd_line_options()
    settings.get_user_input(app_settings)

    # Set photo path and get list of photo file names
    photo_dir_path = helper.get_photo_path()
    img_file_names = helper.get_photo_file_names(photo_dir_path, settings.VALID_FILE_EXT)

    if app_settings.isRandomized:
        random.shuffle(img_file_names)
    else:
        img_file_names = sorted(img_file_names)

    screen_size = ImageGrab.grab().size
    load_initial_photos()

    app_settings.text_font = 'Arial' if platform.system() == 'Windows' else 'Liberation Sans'
    app_settings.print_values()

    # Initialize a display window
    tk_window = Tk()

    try:
        icon = PhotoImage(file=helper.resource_path("icon.png"))
        tk_window.iconphoto(False, icon)
    except Exception:
        pass

    tk_window.title("Simpler SlideShow")
    tk_window.attributes('-fullscreen', isFullscreen)
    tk_window.config(cursor="none")
    tk_window.focus_force()

    # creates/pack label widget onto the root window
    tk_photo_label = Label(
        tk_window,
        anchor=TkinterConstants.CENTER,
        borderwidth="0",
        compound=TkinterConstants.CENTER,
        font=(app_settings.text_font, 50),
        fg='#ef0000',
        bg=app_settings.bg_color
        )
    tk_photo_label.pack(expand=True, fill="both")

    # Create and place photo count label 
    photo_count_label = Label(tk_window, text="0", font=(app_settings.text_font, 15, "bold"), fg="black", bg="white")
    photo_count_label.place(x=10, y=10, anchor="nw")
    
    # Create labels
    pause_label = Label(tk_window, text="PAUSED", font=(app_settings.text_font, 20, "bold"), fg="red", bg="white")
    speed_change_label = Label(tk_window, text="", font=(app_settings.text_font, 35, "bold"), fg="red", bg="white")
    slide_settings_label = Label(tk_window, text=str(app_settings), font=(app_settings.text_font, 10, "bold"), fg="black", bg="white")
    photo_file_name_label = Label(tk_window, text="", font=(app_settings.text_font, 10), fg="black", bg="white")

    # Binding keys to an event/method
    tk_window.bind("<Escape>", exit_slideshow)
    tk_window.bind("<space>", pause_slideshow)
    tk_window.bind("<Down>", slowdown_slideshow)
    tk_window.bind("<Up>", speedup_slideshow)
    tk_window.bind("<Left>", previous_photo)
    tk_window.bind("<Right>", next_photo)
    tk_window.bind("<f>", fullscreen)
    tk_window.bind("<s>", show_settings)
    tk_window.bind("<i>", print_info)

    schedule_next_photo()
    tk_window.mainloop()