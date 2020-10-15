from PIL import Image
from pathlib import Path
from math import log2, ceil # literally the only functions from math needed rn
import json

p = Path(".\\saved_data") # Opens the folder with all of the images in.
image_paths = list(p.glob("*")) # Fetches all files in the saved_data folder. This assumes the folder only has images.
image_num = len(image_paths) + 1 # We add one as I need to have a "blank" image for when a spot in unfilled.
canvas_base = ceil(log2(image_num)) # This figures out the lowest value for x in 2^x where 2^x is greater than image_num. This is used because you generally want things like textures to be ^2

resize_size = 512 # How large we want individual images to be, x and y.


# Create the JSON file that specifies which index each image is at.
i = 1 # The index starts at 1, as 0 is a blank spot.
index_dict = {} # Just a single level dictionary, with image_name=index
index_dict["width"] = canvas_base
for im in image_paths:
	fname = im.name # This gets only the name of the file, and not the full path.
	index_dict[fname] = i
	i += 1
root = [index_dict] # JSON needs to start with an array as its root

with open("image_index.json", "w") as f:
	f.write(json.dumps(index_dict))

# Make collage.
images = []
blank = Image.new("RGBA", (resize_size, resize_size))
images.append(blank) # Creates a blank image to add to the start of the list.
for img in image_paths:
	img_resized = Image.open(img).resize((resize_size, resize_size)) # TODO Maybe mess with resampling to get a better looking image?
	images.append(img_resized) # Adds the Image object to the images array.

empty_spots = (canvas_base**2) - len(images) # Figures out how many more blank images we need to add to fill the canvas.
for i in range(empty_spots):
	images.append(blank)


cols = canvas_base
rows = canvas_base
width = resize_size * canvas_base # New image dimensions
height = resize_size * canvas_base
#size = resize_size, resize_size
new_im = Image.new('RGBA', (width, height))

i = 0
x = 0
y = 0
for row in range(rows):
	for col in range(cols):
		print(i, x, y)
		new_im.paste(images[i], (x, y))
		i += 1
		x += resize_size
	y += resize_size
	x = 0

new_im.save("collage.png")