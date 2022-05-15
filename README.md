<div align="center">
<h1>📸 Simpler SlideShow 📷</h1>
</div>

## Index
- [Origins](#origins)
- [Controls](#controls)
- [Features](#features)
	- [Photo Transformation](#photo-transformation)
	- [Photo Sequence](#photo-sequence)
	- [Background Color](#background-color)
- [Download](#download)

## Origins
With a Raspberry Pi and a TV in the living room collecting dust, I thought it would be neat to build a simplistic barebone slideshow that would run on the Raspi+TV. Plus, my mom has many family/baby photos that she wanted to display somewhere. So, a nice little slideshow gallery on the unused TV would be perfect.

I have the Pi's SSH/VNC enabled and set my router to give the Pi a static IP address (DHCP reservation). This makes it so that I can essentially run a headless setup and access the Pi over the local network. Technically it isn't fully headless because it does have a "monitor/display" (the TV haha). But this makes accessing the Pi much more convenient.

With the somewhat-headless setup, I can:
- Control the slideshow or any other settings on the Pi from the comfort of my room 🙂
- Send photos from my pc to the pi (the `scp` command works like a charm for this)
- Turn off the Pi from my pc

## Controls
| Keys | Description |
| :---: | :--- |
| `SPACE` | pause the slideshow|
| `L_ARW` | slowdown slideshow by intervals of 0.5sec |
| `R_ARW` | speedup slideshow by intervals of 0.5sec  |
| `F` | switch between fullscreen and windowed |
| `ESC` | exit slideshow |

**Note:** The slideshow window needs to be focused for these events to fire. Also, the cursor is hidden on the slideshow.

## Features

Simplicity is the main feature 😀.<br>
However, there are photo transformation and photo display sequence options that add a nice touch to this tool.

### Photo Transformation

- **Resizing:** (default) All images that are loaded will go through some resizing to fit the display as best as possible. Photos that are smaller than the display will scale up and vice versa. The resizing keeps the aspect ratio of the photo which may result in some empty/white spaces on the screen.

- **Resizing & Cropping:** This will fit the photo exactly to the screen using both resizing and cropping. The cropping is a center cropping, this means it will crop an equal amount from both the left and right side (or top/bottom). 

**Note**: Some computers (seems like mostly laptops) will have their recommended scale at 125% (found in `Display Settings`). If the scale is not 100% then the photos will be slightly cut off even when using the `resize` option.

### Photo Sequence

- **Ordered:** The slideshow will cycle through the photos in the order they were loaded.

- **Randomized:** This will randomize the order the photos are displayed. Each photo will be displayed once in a random order till it cycles back again. No photos will be shown more than another during a single loop. For example, if there were 5 photos loaded, then the sequence may look like: `[4,2,5,1,3] -> [1,2,5,3,4] -> [3,4,2,1,5] -> etc`

### Background Color

You are able to change the windows background color. It is only useful when your photos don't find exactly on the screen and there is empty spaces. The empty space is the "background color"

Current Supported Colors:
| Color | Description |
| :---: | :---: |
| `black` | ⚫ |
| `white` | ⚪ |

## Download
Go to [releases](https://github.com/AnthonyN3/simpler-slideshow/releases)

Note: Since this is such a barebone/simple tool, if you have python and the pillow module installed (+ supported version)
then you can just run the source code and alter it to your desire.
