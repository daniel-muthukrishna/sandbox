import os
import imageio.v2 as imageio

images = []

i = -2
for i in range(-2, 59):
    filename = f"/Users/danielmuthukrishna/Documents/Projects/sandbox/make_gifs/2018iyx_timestamp_lcs 4/{i}_2018iyx_lc.png"
    images.append(imageio.imread(filename))
imageio.mimsave('2018iyx_lc_model.gif', images)
