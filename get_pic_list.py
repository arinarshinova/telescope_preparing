import math
import numpy as np
import pandas as pd
from urllib.request import urlopen
from urllib.error import HTTPError
import matplotlib.pyplot as plt
from PyAstronomy import pyasl


def plot_PA(x_c, y_c, shiftx, shifty, angle, add_shiftx, add_shifty, add_angle, length):

        startx = x_c + shiftx - length * math.sin(math.radians(angle))
        starty = y_c + shifty - length * math.cos(math.radians(angle))

        endx = x_c + length * math.sin(math.radians(angle))
        endy = y_c + length * math.cos(math.radians(angle))

        plt.text(startx+length/10, starty, f'PA={angle}', color='white', fontsize=6)
        
        plt.plot([startx, endx], [starty, endy], color='white', lw=0.5)

        if add_angle != 'NaN':
            
            add_startx = x_c + add_shiftx - length * math.sin(math.radians(add_angle))
            add_starty = y_c + add_shifty - length * math.cos(math.radians(add_angle))

            add_endx = x_c + length * math.sin(math.radians(add_angle))
            add_endy = y_c + length * math.cos(math.radians(add_angle))

            plt.text(add_startx+length/10, add_starty, f'PA={add_angle}', color='deepskyblue', fontsize=6)
        
            plt.plot([add_startx, add_endx], [add_starty, add_endy], color='deepskyblue', lw=0.5)


# init all data
names = []           # here the names of the objects (usually use _ except for spaces)
coords = []          # here coordinates hh mm ss.s (s)dd mm ss.s
pos_ang = []         # here position angle of slit in degrees, if it's not nessesary just NaN
add_pos_ang = []     # here additional position angle of slit in degrees, if it's not nessesary just NaN
epoch = []           # here an epoch, usually 2000.0

dict = {'name': names, 'coordinates': coords, 'PA': pos_ang, 'add_PA': add_pos_ang, 'epoch': epoch} 
   
main = pd.DataFrame(dict)

alpha = np.zeros(len(names))
delta = np.zeros(len(names))
k = 0

for i in coords:
    ra, dec = pyasl.coordsSexaToDeg(i)
    alpha[k] = ra
    delta[k] = dec
    k += 1

main['ra'] = alpha
main['dec'] = delta

print(main)

f = open('links.txt', 'a')       # here a file with links to legacy or SDSS, may be useful for creating a document of observations

#plot images
for ind in main.index:
    print(ind)
    try:
        url = f'https://www.legacysurvey.org/viewer/jpeg-cutout?ra={main['ra'][ind]}&dec={main['dec'][ind]}&width=512&height=512&layer=ls-dr10-grz&pixscale=0.7'
        data = plt.imread(urlopen(url), format='jpeg')
        urldata = f'https://www.legacysurvey.org/viewer?ra={main['ra'][ind]}&dec={main['dec'][ind]}&layer=ls-dr9&zoom=13'
        f.write(f'{main['name'][ind]}: {url}\n')
        plt.imshow(data)
        plt.axis('off')
        plot_PA(len(data)/2, len(data)/2, 0, 0, main['PA'][ind], 0, 0, main['add_PA'][ind], 100)
        plt.savefig(f'{main['name'][ind]}_legacy.png', dpi=600, bbox_inches='tight')
        plt.close()

    except HTTPError:
        url = f'https://skyserver.sdss.org/dr18/SkyServerWS/ImgCutout/getjpeg?ra={main['ra'][ind]}&dec={main['dec'][ind]}&scale=0.7&width=512&height=512&opt=%22G%22'
        data = plt.imread(urlopen(url), format='jpeg')
        urldata = f'https://skyserver.sdss.org/dr18/VisualTools/navi?ra={main['ra'][ind]}&dec={main['dec'][ind]}&scale=0.7'
        f.write(f'{main['name'][ind]}: {urldata}\n')
        plt.imshow(data)
        plt.axis('off')
        plot_PA(len(data)/2, len(data)/2, 0, 0, main['PA'][ind], 0, 0, main['add_PA'][ind], 100)
        plt.savefig(f'{main['name'][ind]}_sdss.png', dpi=600, bbox_inches='tight')
        plt.close()

f = open('scorp0210.lst', 'a')       # here name of telescope file
f.write('# Silchenko\n')             # here name of PI

main['rah'] = main['coordinates'].apply(lambda x: " ".join(x.split(' ', 3)[:3]))
main['decd'] = main['coordinates'].apply(lambda x: " ".join(x.split(' ', 3)[3:]))

for ind in main.index:
    main.loc[ind, 'name'] = main.loc[ind, 'name'].replace('_', ' ')
    f.write(f'{main['rah'][ind]}; {main['decd'][ind]}; {main['epoch'][ind]}  # {main['name'][ind]}\n')

f.close()
