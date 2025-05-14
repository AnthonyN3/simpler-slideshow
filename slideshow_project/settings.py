import sys, getopt, re
import helper

MAX_DELAY_MS = 30_000
MIN_DELAY_MS = 500

VALID_FILE_EXT = (".jpeg", ".jpg", ".png", ".tga", ".webp", ".bmp", ".psd")
VALID_FORMATS = ("JPEG", "PNG", "TGA", "WEBP", "BMP", "PSD")

YES_ANS = ("yes", "y", "ya", "ye", "yee", "yup", "yuh", "yeah", "okay", "ok", "yep", "yea", "alright", "roger", "oui", "sure")
BG_COLOR_OPTIONS = ("white", "black", "red", "green", "blue", "cyan", "yellow", "magenta")

class SlideSettings:
    def __init__(self, isRandomized: bool, isCropped: bool, delay_ms: int, bg_color: str):
        self.isRandomized = isRandomized
        self.isCropped = isCropped
        self.delay_ms = delay_ms
        self.bg_color = bg_color
    
    def print_values(self):
        print("\n RESIZING = ENABLED")
        print(" CROPPING = " + ("ENABLED" if self.isCropped else "DISABLED" ))
        print(" RANDOMIZATION = " + ("ENABLED" if self.isRandomized else "DISABLED" ))
        print(" DELAY = " + str(round(self.delay_ms/1000, 1)) +" sec")
        if self.bg_color:
            print(" BG COLOR = " + self.bg_color)
        print("\n")
            

def get_cmd_line_options() -> SlideSettings:
    args = sys.argv[1:]
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

            isRandomize = None
            isCropped = None
            delay_ms = None
            bg_color = None

            for opt, val in option_value:
                if opt in ("-h", "--help"):
                    helper.print_help()
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
                    if val.lower() in BG_COLOR_OPTIONS:
                        bg_color = val.lower()
                    elif re.search("^([0-9a-fA-F]{3}){1,2}$", val):
                        bg_color = '#' + val
                    else:
                        print("Invalid background color specified for --bg_color/-b")
                        print(f"Type {sys.argv[0]} --help to see a list of options")
                        sys.exit()
                elif opt in ("-t", "--timer"):
                    if helper.is_number(val):
                        delay_input = int(round(float(val),1) * 1000) #convert second to ms
                        if delay_input > MAX_DELAY_MS:
                            print(f"Speed cannot be over {helper.ms_to_sec(MAX_DELAY_MS)} seconds")
                            sys.exit()
                        elif delay_input < MIN_DELAY_MS:
                            print(f"Speed cannot be under {helper.ms_to_sec(MIN_DELAY_MS)} seconds")
                            sys.exit()
                        else:
                            delay_ms = delay_input
                    else:
                        print("invalid value for --speed/-s")
                        print(f"Type {sys.argv[0]} --help to see a list of options")
                        sys.exit()

            return SlideSettings(isRandomized=isRandomize, isCropped=isCropped, delay_ms=delay_ms, bg_color=bg_color)
        
        except getopt.error as e:
            print(e)
            print(f"\nUsage: {sys.argv[0]} [OPTIONS]")
            print(f"Type {sys.argv[0]} --help to see a list of options")
            sys.exit()

    else:
        return SlideSettings(isRandomized=None, isCropped=None, delay_ms=None, bg_color=None)

def get_user_input(settings: SlideSettings):
    if settings.delay_ms == None:
        delay_input = input("\n Input slideshow speed in seconds: ")

        # converts sec to ms and rounds down to nearest full second or half a second (0.5,1,1.5,etc)
        if helper.is_number(delay_input):
            # round one dec place and convert sec to ms 
            delay_input = int(round(float(delay_input),1) * 1000)

            if delay_input >= MAX_DELAY_MS:
                delay_ms = MAX_DELAY_MS
            elif delay_input <= MIN_DELAY_MS:
                delay_ms = MIN_DELAY_MS
            else:
                rem = delay_input % 500
                delay_ms = delay_input-rem if rem else delay_input
            settings.delay_ms = delay_ms
        else:
            settings.delay_ms = 4500

    print(" SPEED: " + str(round(settings.delay_ms/1000, 1)) +" sec")

    if settings.isCropped == None:
        settings.isCropped = input("\n Would you like the photos to be Cropped to fit? [y/n] ").lower() in YES_ANS
        print(" CROP:", settings.isCropped)
    if settings.isRandomized == None:
        settings.isRandomized = input("\n Would you like photo sequence to be Randomized? [y/n] ").lower() in YES_ANS
        print(" RANDOMIZED:", settings.isRandomized)
    if not settings.isCropped and settings.bg_color == None:
        bg_color_input = input(f"\n {BG_COLOR_OPTIONS} | or hex color (ex. #FF22AA)\n Input background color: ").lower()
        if  (bg_color_input in BG_COLOR_OPTIONS) or (re.search("^#([0-9a-fA-F]{3}){1,2}$", bg_color_input)):
            settings.bg_color = bg_color_input
        else:
            settings.bg_color = "black"