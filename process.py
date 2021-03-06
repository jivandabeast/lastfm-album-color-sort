# ---
# Taken from SamPom100 on GitHub
# https://github.com/SamPom100/SortImagesByColor
# 
# Edits made by me to give credit/clean up the code
# ---

from __future__ import print_function
from math import sqrt
import binascii
import struct
from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import webcolors
import os
import glob

NUM_CLUSTERS = 5

COLORS = (
    (255, 0, 0),  # red
    (255, 125, 0),  # orange
    (255, 255, 0),  # yellow
    (125, 255, 0),  # spring green
    (0, 255, 0),  # green
    (0, 255, 125),  # turquoise
    (0, 0, 255),  # cyan
    (0, 125, 255),  # ocean
    (0, 0, 255),  # blue
    (125, 0, 255),  # violet
    (255, 0, 255),  # magenta
    (255, 0, 125),  # raspberry
    (-50, -50, -50),  # black
    (300, 300, 300),  # white
)

COLOR_NAMES = {
    (255, 0, 0): "red",
    (255, 125, 0):  "orange",
    (255, 255, 0):  "yellow",
    (125, 255, 0):  "spring green",
    (0, 255, 0):  "green",
    (0, 255, 125):  "turquoise",
    (0, 0, 255):  "cyan",
    (0, 125, 255):  "ocean",
    (0, 0, 255):  "blue",
    (125, 0, 255):  "violet",
    (255, 0, 255):  "magenta",
    (255, 0, 125):  "raspberry",
    (-50, -50, -50):  "black",
    (300, 300, 300):  "white",
}

colorFolders = ["red", "orange", "yellow", "spring green", "green", "turquoise", "cyan", "ocean", "blue", "violet", "magenta", "raspberry", "black", "white"]

def get_closest_color(rgb):
    r, g, b = rgb
    color_diffs = []
    for color in COLORS:
        cr, cg, cb = color
        color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
        color_diffs.append((color_diff, color))
    return COLOR_NAMES.get(min(color_diffs)[1])

def getDominantColor(img, filename):
    try:
        im = img.resize((100, 100))
        ar = np.asarray(im)
        shape = ar.shape
        ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)
        codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
        vecs, dist = scipy.cluster.vq.vq(ar, codes)
        counts, bins = np.histogram(vecs, len(codes))
        index_max = np.argmax(counts)
        peak = codes[index_max]
        color = binascii.hexlify(bytearray(int(c)
                                           for c in peak)).decode('ascii')
        rgb = ImageColor.getcolor('#'+color, "RGB")
        colorName = get_closest_color(rgb)
        img.save('output/'+colorName+'/'+filename, 'PNG')
        return(filename + ' is '+colorName)
    except Exception as e:
        # print(filename + ' was broken')
        print('Error:', e)

def verify_dirs():
    # Verify and correct file structure
    if not os.path.exists('input'):
        os.makedirs('input')

    if not os.path.exists('output'):
        os.makedirs('output')

    for color in colorFolders:
        if not os.path.exists('output/' + str(color)):
            os.makedirs('output/' + str(color))
    return None

def sort_colors():
    path, dirs, files = next(os.walk('input/'))
    file_count = len(files)
    count = 1
    for filename in glob.glob('input/*'):
        try:
            im = Image.open(filename)
            temp = getDominantColor(im, str(filename[6:]))
            # print('('+str(count)+'/'+str(file_count)+') , '+temp)
            count = count+1
        except Exception as e:
            # print(str(filename) + ' is not an image')
            print('Error: ', e, filename)