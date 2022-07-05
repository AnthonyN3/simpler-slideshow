import sys, os, platform
import getopt, re, random
from tkinter import *
from PIL import Image, ImageTk, ImageGrab, ImageOps

def exit_slideshow(event=None):
	root.destroy()

def fullscreen(event=None):
	global isFullscreen
	root.attributes('-fullscreen', not isFullscreen)
	isFullscreen = not isFullscreen

# possible race condition? after/after_cancel
def pause_slideshow(event=None):
	global isPause, photo_task_id
	if isPause:
		isPause = False
		label_image.config(text="")
		# Restart loop with half the specified delay for the first photo
		photo_task_id = root.after(round(delay_ms/2), next_photo_rnd if isRandomize else next_photo_order)
	else:
		isPause = True
		if "text_task_id" in globals():
			root.after_cancel(text_task_id)
		stop_slideshow()
		label_image.config(text="PAUSED")

def display_speed(speed_ms):
	global text_task_id
	if "text_task_id" in globals():
		root.after_cancel(text_task_id)
	label_image.config(text="\n\n\n\n\n" + ms_to_sec(speed_ms) + " seconds")
	text_task_id = root.after(1000, remove_text)

def remove_text():
	label_image.config(text="")


def next_photo(event=None):
	global list_count, list_count_history, count, index
	# Note: The next/previous control functionality adds more complexity to my original method
	# of using a stack data structure for the photo randomization. It would be much simpler to use list indexing instead. 
	if isRandomize:
		if not list_count:
			list_count = generate_list(num_of_img)
			list_count_history = []
		temp_index = index
		index = list_count.pop()
		if temp_index == index:
			if not list_count:
				list_count = generate_list(num_of_img)
				list_count_history = []
			else:
				list_count_history.append(index)
			index = list_count.pop()
		list_count_history.append(index)
		label_image.config(image=images[index])
	else:
		if count >= num_of_img - 1:
			count = -1
		count = count + 1
		label_image.config(image=images[count])

def previous_photo(event=None):
	global list_count, list_count_history, count, index
	if isRandomize:
		if list_count_history:
			if index == list_count_history[-1]:
				if len(list_count_history) > 1:
					list_count.append(list_count_history.pop())
					index = list_count_history.pop()
					list_count.append(index)
					label_image.config(image=images[index])
			else:
				index = list_count_history.pop()
				list_count.append(index)
				label_image.config(image=images[index])
			
	else:
		if count <= 0:
			count = num_of_img
		count = count - 1
		label_image.config(image=images[count])

def speedup_slideshow(event=None):
	if not isPause:
		global delay_ms
		if(delay_ms > min_delay_ms):
			delay_ms = delay_ms - 500
			display_speed(delay_ms)
			reset_timer()

def slowdown_slideshow(event=None):
	if not isPause:
		global delay_ms
		if(delay_ms < max_delay_ms):
			delay_ms = delay_ms + 500
			display_speed(delay_ms)
			reset_timer()

def generate_list(size):
	li = list(range(size))
	random.shuffle(li)
	return li

def start_slideshow():
	next_photo_rnd() if isRandomize else next_photo_order()

def stop_slideshow():
	if "photo_task_id" in globals():
		root.after_cancel(photo_task_id)

def reset_timer():
	global photo_task_id
	root.after_cancel(photo_task_id)
	if isRandomize:
		photo_task_id = root.after(delay_ms, next_photo_rnd)
	else:
		photo_task_id = root.after(delay_ms, next_photo_order)

def next_photo_order():
	global count, photo_task_id
	if count >= num_of_img - 1:
		count = -1
	count = count + 1	# increment needs to be above the config set so the next/previous controls sync
	label_image.config(image=images[count])
	photo_task_id = root.after(delay_ms, next_photo_order)

def next_photo_rnd():
	global list_count, photo_task_id, list_count_history, index
	if not list_count:
		list_count = generate_list(num_of_img)
		list_count_history = []
	index = list_count.pop()
	list_count_history.append(index)
	label_image.config(image=images[index])
	photo_task_id = root.after(delay_ms, next_photo_rnd)

def is_number(num):
	try:
		float(num)
		return True
	except ValueError:
		return False

# Rounded to nearest decimal place
def ms_to_sec(ms):
	return str(round(ms/1000,1))

def print_controls():
	print("\n ------------------ CONTROLS ------------------")
	print("         ^ - speed up  | max=" + ms_to_sec(max_delay_ms) + " sec")
	print("         v - slow down | min=" + ms_to_sec(min_delay_ms) + " sec")
	print("        <- - previous photo")
	print("        -> - next photo")
	print("         F - fullscreen")
	print("       ESC - exit")
	print("     SPACE - pause")
	print(" ----------------------------------------------")

def print_help():
	print("Usage: simpler-slideshow [OPTIONS]")
	print("\nOptions:")
	print("  General Options:")
	print("    -f, --fit                  Resize all photos to fit the screen\n\
                               while keeping the photos aspect ratio")
	print("    -c, --crop                 Crops & resize all photos to fit\n\
                               the screen leaving no empty spaces\n\
                               on the screen")
	print("    -r, --randomize            Displays the photos in a random order")
	print("    -o, --order                Displays the photos in the order they\n\
                               were loaded in")
	print("    -b, --bg-color COLOR       Specify background color: \"black\",\n\
                               \"white\", \"red\", \"green\", \"blue\",\n\
                               \"cyan\", \"yellow\", \"magenta\" or \n\
                               use hex colors ie: \"FF0000\". Omit the #")
	print("    -t, --timer SECONDS        Specify slideshow time between photos\n\
                               in seconds. Will round to nearest half\n\
                               or full second. ie: 1.0, 1.5, 2.0, etc")
	print("\nNote: --fit and --crop can't be used together\n      --randomize and --order can't be used together")

# Variables
max_delay_ms = 30000
min_delay_ms = 500
delay_ms = 4500
isPause = False
isFullscreen = True
count = -1
index = 0
list_count = []
list_count_history = []
num_of_img = 0
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "Photos", "")
valid_formats = ("JPEG", "PNG", "TGA", "WEBP", "BMP", "PSD") # "python3 -m PIL" to list all supported formats or run "PIL.features.pilinfo()"
yes_ans = ("yes", "y", "ya", "ye", "yee", "yup", "yuh", "yeah", "okay", "ok", "yep", "yea", "alright", "roger", "oui", "sure") # lol
color_list = ("white", "black", "red", "green", "blue", "cyan", "yellow", "magenta")
images = []

# User inputs
delay_input = None
isCropped = None
isRandomize = None
bg_color = None

args = sys.argv[1:]

# checks if options are used and apply them accordingly
if args:
	try:
		option_value, arg_val = getopt.getopt(
			args, 
			"hrocfb:t:", 
			["help","randomize", "order", "crop", "fit", "bg-color=", "timer="]
			)

		if arg_val:
			print("Illegal arguments:", arg_val)
			print(f"Type {sys.argv[0]} --help to see a list of options")
			sys.exit()

		# Error message if certain options are used together
		i = [x[0] for x in option_value]
		if ("-c" in i or "--crop" in i) and ("-f" in i or "--fit" in i):
			print("Cannot use option \"--crop\" and \"--fit\" together")
			print(f"Type {sys.argv[0]} --help to see a list of options")
			sys.exit()
		if ("-r" in i or "--randomize" in i) and ("-o" in i or "--order" in i):
			print("Cannot use option \"--randomize\" and \"--order\" together")
			print(f"Type {sys.argv[0]} --help to see a list of options")
			sys.exit()

		for opt, val in option_value:
			if opt in ("-h", "--help"):
				print_help()
				sys.exit()
			elif opt in ("-r", "--randomize"):
				isRandomize = True
			elif opt in ("-o", "--order"):
				isRandomize = False
			elif opt in ("-c", "--crop"):
				isCropped = True
			elif opt in ("-f", "--fit"):
				isCropped = False
			elif opt in ("-b", "--bg-color"):
				if val.lower() in color_list:
					bg_color = val.lower()
				elif re.search("^([0-9a-fA-F]{3}){1,2}$", val):
					bg_color = '#' + val
				else:
					print("Invalid background color specified for --bg_color/-b")
					print(f"Type {sys.argv[0]} --help to see a list of options")
					sys.exit()
			elif opt in ("-t", "--timer"):
				if is_number(val):
					delay_input = int(round(float(val),1) * 1000) #convert second to ms
					if delay_input > max_delay_ms:
						print(f"Speed cannot be over {ms_to_sec(max_delay_ms)} seconds")
						sys.exit()
					elif delay_input < min_delay_ms:
						print(f"Speed cannot be under {ms_to_sec(min_delay_ms)} seconds")
						sys.exit()
					else:
						delay_ms = delay_input
				else:
					print("invalid value for --speed/-s")
					print(f"Type {sys.argv[0]} --help to see a list of options")
					sys.exit()		
	except getopt.error as e:
		print(e)
		print(f"\nUsage: {sys.argv[0]} [OPTIONS]")
		print(f"Type {sys.argv[0]} --help to see a list of options")
		sys.exit()

print_controls()

if delay_input == None:
	delay_input = input("\n Input slideshow speed in seconds: ")

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

	print(" SPEED: " + str(round(delay_ms/1000, 1)) +" sec")

if isCropped == None:
	isCropped = input("\n Would you like the photos to be Cropped to fit? [y/n] ").lower() in yes_ans
	print(" CROP:", isCropped)
if isRandomize == None:
	isRandomize = input("\n Would you like photo sequence to be Randomized? [y/n] ").lower() in yes_ans
	print(" RANDOMIZE:", isRandomize)
if not isCropped and bg_color == None:
	bg_color_input = input(f"\n {color_list} | or hex color (ex. #FF22AA)\n Input background color: ").lower()
	if  (bg_color_input in color_list) or (re.search("^#([0-9a-fA-F]{3}){1,2}$", bg_color_input)):
		bg_color = bg_color_input
	else:
		bg_color = "black"

# Initialize a display window
root = Tk()
root.title("Simpler SlideShow")
root.attributes('-fullscreen', True)
root.config(cursor="none", bg=bg_color)
root.focus_force()

# creates/pack label widget onto the window "root"
label_image = Label(
	root,
	anchor=CENTER,
	borderwidth="0",
	compound=CENTER,
	font=('Arial' if platform.system() == 'Windows' else 'Liberation Mono',50),
	fg='#ef0000'
	)
label_image.pack()

# Binding keys to an event
root.bind("<Escape>", exit_slideshow)
root.bind("<space>", pause_slideshow)
root.bind("<Down>", slowdown_slideshow)
root.bind("<Up>", speedup_slideshow)
root.bind("<Left>", previous_photo)
root.bind("<Right>", next_photo)
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
		if isCropped:
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
print(" CROPPING = " + ("ENABLED" if isCropped else "DISABLED" ))
print(" RANDOMIZATION = " + ("ENABLED" if isRandomize else "DISABLED" ))
print(" DELAY = " + str(round(delay_ms/1000, 1)) +" sec\n")

start_slideshow()
root.mainloop() # tkinter runs event loop and halts on this line till root window is closed. Also, allows for listening to events 
