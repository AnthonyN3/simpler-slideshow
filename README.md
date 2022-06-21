<div align="center">
<h1>📷 Simpler SlideShow 🖼</h1>
</div>

## Index
- [Inspo and Info](#inspo-and-info)
- [Controls](#controls)
- [Features](#features)
	- [Photo Transformation](#photo-transformation)
	- [Photo Sequence](#photo-sequence)
	- [Background Color](#background-color)
- [Download](https://github.com/AnthonyN3/simpler-slideshow/releases)

## Inspo and Info
I thought it would be nice to build a simplistic  slideshow application using Python. Moreover, my parents have many family photos they wanted to display somewhere in the house. So, I thought a TV slideshow gallery would be perfect. To do so, I'd just need to create a slideshow app and run it on a raspberry pi connected to a TV.

Technically, the slideshow can run on any kind of device like a generic windows computer. But I believe the most cost effective and efficient hardware for this use-case would be a raspberry pi. <br> Advantages of using Pi:
1. Uses less power and therefore less 💲
2. Lightweight fast hardware/OS, it would be overkill to use a good computer and annoying to use a slow computer.
3. Linux is easier to customize. For example, setting up ssh server to access the Pi or making the Pi run the app on startup.

I have the Pi's SSH/VNC enabled and set my router to give the Pi a static IP address (DHCP reservation). This makes it so that I can essentially run a headless setup and access the Pi over the local network. Technically, it isn't fully headless because it does have a "display" (the TV lol). But this makes accessing the Pi much more convenient.

With this setup, I have full access to the Pi from any device on the same local network and can:
- Control the slideshow or any other settings on the Pi (from the comfort of my room 🛌💤)
- Send photos from my pc to the Pi through the local network. This removes the pain in physically transferring photos using one of the Pi's usb ports.

## Controls
| Keys | Description |
| :---: | :--- |
| `SPACE` | pause slideshow|
| `↑` | speedup slideshow by intervals of 0.5sec |
| `↓` | slowdown slideshow by intervals of 0.5sec |
| `←` | previous photo |
| `→` | next photo |
| `F` | switch between fullscreen and windowed |
| `ESC` | exit slideshow |

**Notes:**

The slideshow window needs to be focused for these controls to work. Also, the cursor is hidden on the slideshow.

If the slideshow is using randomization, the "previous photo" (←) control will halt once it reaches the first photo in its current loop. This is a design choice and is due to how the randomization was implemented. Read about the **randomized** function below.


## Features

Simplicity is the main feature 😀.<br>
However, there are photo transformation and display sequence options that add a nice touch.

### Photo Transformation

- **Resizing:** (default) All images that are loaded will go through some resizing to fit the display as best as possible. Photos that are smaller than the display will scale up and if larger will scale down. The resizing keeps the aspect ratio of the photo which may result in some empty spaces on the screen.

- **Resizing & Cropping:** This will make the photo take up the entire space of the screen using both resizing and cropping. The cropping is a center cropping, meaning it will crop an equal amount from both the left and right (or top/bottom).

**Note**: I've noticed some window computers (mostly laptops) will have their default scale at 125% (found in `Display Settings`). If the scale is not 100%, then the photos will be slightly cut off even when using the `resize` option.

### Photo Sequence

- **Ordered:** The slideshow will cycle through the photos in the order they were loaded.

- **Randomized:** This will randomize the order the photos are displayed. Each photo will be displayed once until all photos are shown, then the photos are shuffled and the process repeats. No one photo will be shown more than another during a single loop. For example, if there are 5 photos loaded, then the sequence may look like: <br>`[4,2,5,1,3] -> [1,2,5,3,4] -> [3,4,2,1,5] -> etc`

### Background Color

You can change the color of the background. The background is the empty space the photo does not take up.

Current Supported Colors:
| Color | Description |
| :---: | :---: |
| `black` | ⚫ |
| `white` | ⚪ |
| `red` | 🔴 |
| `green` | 🟢 |
| `blue` | 🔵 |
| `cyan` | 🔵 |
| `yellow` | 🟡 |
| `magenta` | 🟣 |
| `hex value` | 🌈 |