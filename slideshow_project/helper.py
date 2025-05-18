import random
import os
import sys

def print_controls(min_delay_ms: int, max_delay_ms: int):
	print("\n ------------------ CONTROLS ------------------")
	print("         ^ - speed up  | max=" + ms_to_sec(max_delay_ms) + " sec")
	print("         v - slow down | min=" + ms_to_sec(min_delay_ms) + " sec")
	print("        <- - previous photo")
	print("        -> - next photo")
	print("         F - fullscreen")
	print("       ESC - exit")
	print("     SPACE - pause")
	print("         S - show slide setting values")
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
	
def is_number(num):
	try:
		float(num)
		return True
	except ValueError:
		return False

# Rounded to nearest decimal place
def ms_to_sec(ms):
	return str(round(ms/1000,1))

def get_photo_path() -> str:
	# Getting the current path is dependent on if it's a python script or a executable (pyinstaller)
	if getattr(sys, 'frozen', False):
		return os.path.join(os.path.dirname(sys.executable), "photos", "")
	else:
		return os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos", "")
	
def get_photo_file_names(path: str, file_ext: tuple):
    try:
        return [f for f in os.listdir(path) if f.lower().endswith(file_ext)]
    except Exception as e:
        print(" [ERROR FETCHING PHOTO FILE NAMES] -", e)
        print(" Terminating Program...")
        sys.exit()

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return filename