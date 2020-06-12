from __future__ import print_function
import binascii
import struct
from PIL import Image, ImageColor
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import cv2


def is_same_color(rgb, rgb_):
    diff = 0
    for i in range(0,3):
        d = rgb[i]-rgb_[i]
        if d<0: d=-d
        if d>70:
            return -1
        diff += d
    return diff

def color():
    NUM_CLUSTERS = 6

    print('reading image')
    im = Image.open('test2.jpg')

    img = im.convert("RGB")

    rgb = img.getpixel((10,10))

    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

    print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = np.histogram(vecs, len(codes))    # count occurrences
    print(counts)
    index_max = np.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    rgb_ = ImageColor.getrgb("#"+colour)
    colors = []
    while len(colors)<4 and NUM_CLUSTERS>-1:
        NUM_CLUSTERS-=1
        counts[index_max]=0
        index_max = np.argmax(counts)                    # find most frequent
        peak = codes[index_max]
        colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        rgb_ = ImageColor.getrgb("#"+colour)
        s = is_same_color(rgb,rgb_)
        print(type(colour))
        if s > 150 or s == -1: colors.append(rgb_)
    print('most frequent is %s (#%s)' % (peak, colour))
    print(colors)
    print(rgb)

if __name__ == "__main__":
    color()