import os
import sys
import random
from tkinter import *
from PIL import Image, ImageTk, ImageGrab, ImageOps

def exit_slideshow(event=None):
	root.destroy()

def fullscreen(event=None):
	global isFullscreen
	root.attributes('-fullscreen', not isFullscreen)
	isFullscreen = not isFullscreen

def pause_slideshow(event=None):
	global isPause
	if isPause:
		isPause = False
		print("UnPaused")
	else:
		isPause = True
		print("Paused")

def speedup_slideshow(event=None):
	global delay_ms
	if(delay_ms > min_delay_ms):
		delay_ms = delay_ms - 500
	print("delay: " + str(delay_ms) + "ms")

def slowdown_slideshow(event=None):
	global delay_ms
	if(delay_ms < max_delay_ms):
		delay_ms = delay_ms + 500
	print("delay: " + str(delay_ms) + "ms")

def generate_list(size):
	li = list(range(size))
	random.shuffle(li)
	return li

def next_photo_order():
	global count
	if count == (num_of_img):
		count = 0
	if(not isPause):
		label_image.config(image=images[count])
		count = count + 1
	root.after(delay_ms, next_photo_order)

def next_photo_rnd():
	global list_count
	if not list_count:
		list_count = generate_list(num_of_img)
	if(not isPause):
		label_image.config(image=images[list_count.pop()])
	root.after(delay_ms, next_photo_rnd)

def is_number(num):
	try:
		float(num)
		return True
	except ValueError:
		return False

# Variables
max_delay_ms = 30000
min_delay_ms = 500
delay_ms = 4500
isPause = False
isFullscreen = True
count = 0
list_count = []
num_of_img = 0
window_bg = "black"

path = "./Photos/"
valid_formats = ("JPEG", "PNG", "TGA", "WEBP", "BMP", "PSD") # "python3 -m PIL" to list all supported formats or run "PIL.features.pilinfo()"
yes_ans = ["yes", "y", "ya", "ye", "yee", "yup", "yuh", "yeah", "okay", "ok", "yep", "yea", "alright", "roger", "oui", "sure"] # lol
images = []

# Message Info/Prompt
print("\n Valid Formats: " + str(valid_formats))
print("\n ------------------ CONTROLS ------------------")
print("     SPACE - pause slideshow")
print("  LEFT_ARW - slow down slideshow | min=" + str(round(min_delay_ms/1000,1)) + " sec")
print("  LEFT_ARW - speed up slideshow  | max=" + str(round(max_delay_ms/1000,1)) + " sec")
print("         F - fullscreen")
print("       ESC - exit slideshow")
print(" ----------------------------------------------")

delay_input = input("\n Input delay/speed in seconds: ")

# checks if user inputs a valid number
# converts sec to ms and rounds down to nearest full second or half a second (0.5,1,1.5,etc)
if is_number(delay_input):
	# round one dec place and convert sec to ms 
	delay_input = int(round(float(delay_input),1) * 1000)
	
	if delay_input >= max_delay_ms:
		delay_ms = max_delay_ms
	elif delay_input <= min_delay_ms:
		delay_ms = min_delay_ms
	else:
		rem = delay_input % 500
		delay_ms = delay_input-rem if rem else delay_input

print(" DELAY = " + str(round(delay_ms/1000, 1)) +" sec")

crop_img = input("\n Would you like the photos be Cropped to fit? [y/n] ").lower() in yes_ans
randomize_img = input(" Would you like photo sequence to be Randomized? [y/n] ").lower() in yes_ans

if not crop_img:
	if input(" Black or white Background? [b/w] ").lower() == 'w':
		window_bg = "white"
	else:
		window_bg = "black"

# Initialize a display window
root = Tk()
root.title("Simpler SlideShow")
root.attributes('-fullscreen', True)
root.config(cursor="none", bg=window_bg)

# creates/pack label widget onto the window "root"
label_image = Label(root, anchor=CENTER, borderwidth="0")
label_image.pack()

# Binding keys to an event
root.bind("<Escape>", exit_slideshow)
root.bind("<space>", pause_slideshow)
root.bind("<Left>", slowdown_slideshow)
root.bind("<Right>", speedup_slideshow)
root.bind("<f>", fullscreen)

screen_size = ImageGrab.grab().size
print("\n ***** Detected Screen Size: " + str(screen_size) + " *****")

# Get the list of all files and directories
try:
	file_names = os.listdir(path)
except Exception as e:
	print(" [ERROR] -", e)
	print(" Terminating Program...")
	sys.exit()

print(" ***** Detected " + str(len(file_names)) + " file(s) in " + path + " *****\n")

for file_name in file_names:
	# using "x=file_name.split('.')[-1]" and if(x in ['jpg', 'png', ...]) would be slightly more efficient than try/except
	# in the case that many exceptions are raised (file cannot be opened)
	try:
		img = Image.open(fp = path + file_name, formats=valid_formats)

		# Checks if the orientation tag present isn't 1 (no tranpose needed)
		isTransposed = False if img.getexif().get(0x0112) == 1 else True # 2-8 means the image has a orientation tag that programs apply when viewing

		# I found checking for orientation tag saves a couple seconds rather than applying exif_transpose on all images and returning a copy
		if isTransposed:
			img = ImageOps.exif_transpose(img) #  applies orientation transpose

		# Reize and Crops OR Resize only
		if crop_img:
			img = ImageOps.fit(image=img, size=screen_size, method=Image.Resampling.LANCZOS)
		else:
			img = ImageOps.contain(image=img, size=screen_size, method=Image.Resampling.LANCZOS)

		images.append(ImageTk.PhotoImage(img))
		print(" +[LOADED] -", file_name, ("(photo transposed)" if isTransposed else '') ) 
	except Exception as e:
		print(" -[FAILED] -", e)

num_of_img = len(images)

print("\n ***** " + str(num_of_img) + " photo(s) loaded *****\n")

# Exits one or les photos were loaded
if num_of_img <= 1:
	print(" Not enough photos found, exiting...")
	root.destroy()
	sys.exit()

print(" RESIZING = ENABLED")
print(" CROPPING = " + ("ENABLED" if crop_img else "DISABLED" ))
print(" RANDOMIZATION = " + ("ENABLED" if randomize_img else "DISABLED" ))
print(" DELAY = " + str(round(delay_ms/1000, 1)) +" sec\n")

# Chooses between if the slideshow will randomly display photos or in the sequience it was loaded in
next_photo_rnd() if randomize_img else next_photo_order()
root.mainloop() # tkinter runs event loop and halts on this line till root window is closed. Also, allows for listening to events 
