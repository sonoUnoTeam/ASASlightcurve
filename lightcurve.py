"""
Created on 2022

@author: sonounoteam (view licence)
"""
# General imports
import pandas as pd
import argparse
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
# Local imports
from data_transform import predef_math_functions as _math
from sound_module.simple_sound import simpleSound
# Instanciate the sonoUno clases needed
_simplesound = simpleSound()
# Sound configurations, predefined at the moment
_simplesound.reproductor.set_continuous()
_simplesound.reproductor.set_waveform('sine')  # piano; sine
_simplesound.reproductor.set_time_base(0.03)
_simplesound.reproductor.set_min_freq(380)
_simplesound.reproductor.set_max_freq(800)
# Parser for command line inputs
parser = argparse.ArgumentParser()
# Receive the directory path from the arguments
parser.add_argument("-d", "--directory", type=str,
                    help="Indicate a directory to process as batch.")
# Indicate the star type
parser.add_argument("-s", "--star-type", type=str,
                    help="Indicate the star type to plot (RWPhe, V0748Cep, ZLep, CGCas, HWPup, MNCam)",
                    choices=['RWPhe', 'V0748Cep', 'ZLep', 'CGCas', 'HWPup', 'MNCam'])
args = parser.parse_args()
path = args.directory
starType = args.star_type
# Read the data as DataFrame
data = pd.read_csv(path)
toplot = data.copy()
# Constants of some selected variable stars
if starType == 'CGCas':
    """https://asas-sn.osu.edu/variables/753bdd73-38a7-5e43-b6c0-063292c7f28d"""
    periodo = 4.3652815
    t0 = 2457412.70647
    BPRP = 0.719
elif starType == 'RWPhe':
    """https://asas-sn.osu.edu/variables/dfa51488-c6b7-5a03-abd4-df3c28273250"""
    periodo = 5.4134367
    t0 = 2458053.49761
    BPRP = 0.586
elif starType == 'V0748Cep':
    """https://asas-sn.osu.edu/variables/dfcbcf52-8a62-542f-9383-1c712d7c042c"""
    periodo = 2.5093526
    t0 = 2458024.93242
elif starType == 'ZLep':
    """https://asas-sn.osu.edu/variables/70cc7024-5027-52f9-a834-75c51f4a5064"""
    periodo = 0.9937068
    t0 = 2457699.6236
elif starType == 'MNCam':
    """https://asas-sn.osu.edu/variables/c3faa9d0-6e10-5775-8bb0-075defcd2578"""
    periodo = 8.1796049
    t0 = 2458046.08639
elif starType == 'HWPup':
    """https://asas-sn.osu.edu/variables/2083f661-73f5-512f-aee5-fd7ad26d5b30"""
    periodo = 13.4590914
    t0 = 2457786.63153
else:
    print('Error en el tipo de estrella.')
# Math to generate the phase diagram
toplot['hjd'] = ((data['hjd'] - t0) / periodo)
toplot['hjd'] = (toplot['hjd'] - toplot['hjd'].astype(int))
# Setting the phase from 0 to 1 and reorganizing the table
count = 0
for i in toplot['hjd']:
    if i < 0:
        toplot.loc[count,'hjd'] = i + 1
    count = count + 1
toplot['hjd'] = toplot['hjd'] + BPRP
count = 0
for i in toplot['hjd']:
    if i > 1:
        toplot.loc[count,'hjd'] = i - 1
    count = count + 1
toplotlength = count
for i in toplot['hjd']:
    toplot.loc[count,'hjd'] = i + 1
    toplot.loc[count, 'camera'] = toplot.loc[count-toplotlength, 'camera']
    toplot.loc[count, 'mag'] = toplot.loc[count-toplotlength, 'mag']
    toplot.loc[count, 'mag_err'] = toplot.loc[count-toplotlength, 'mag_err']
    toplot.loc[count, 'flux'] = toplot.loc[count-toplotlength, 'flux']
    toplot.loc[count, 'flux_err'] = toplot.loc[count-toplotlength, 'flux_err']
    count = count + 1
# Separate the array by camera (the camera name depends on the star type)
groups = toplot.groupby('camera')
if starType == 'CGCas':
    bd_toplot = groups.get_group('bd')
    bc_toplot = groups.get_group('bc') 
elif starType == 'RWPhe':
    be_toplot = groups.get_group('be')
    bf_toplot = groups.get_group('bf') 
else:
    print('Error en el tipo de estrella para separar por grupos.')
# Initialize the plot
fig = plt.figure()
ax = plt.axes()
fig2 = plt.figure()
ax2 = plt.axes()
ax.set_xlabel('Phase')
ax.set_ylabel('Mag')
ax.invert_yaxis()
ax2.set_xlabel('Phase')
ax2.set_ylabel('Mag')
ax2.invert_yaxis()
rep = True

def reproduction(camera1, camera2, camera1text, camera2text, wav_path):
    alldata = pd.concat([camera1, camera2])
    alldata = alldata.sort_values('hjd')
    x_norm, y_norm, status, Error = _math.normalize(alldata['hjd'], alldata['mag'])
    y_norm = y_norm.reset_index()

    if rep:
        ordenada = np.array([alldata['mag'].min(), alldata['mag'].max()])
        count = 0
        value = _simplesound.invert_values_to_sound(y_norm['mag'])
        for index, row in alldata.iterrows():
            abscisa = np.array([row['hjd'], row['hjd']])
            red_line = ax.plot(abscisa, ordenada, 'r')
            red_line2 = ax2.plot(abscisa, ordenada, 'r')
            #plt.pause(0.05)
            # Make the sound
            if row['camera'] == camera1text:
                _simplesound.reproductor.set_waveform('sine')
                #_simplesound.make_bisound(value[count])
                _simplesound.array_bisound(value[count], count, 1, 0)
            elif row['camera'] == camera2text:
                _simplesound.reproductor.set_waveform('square')
                #_simplesound.make_bisound(value[count])
                _simplesound.array_bisound(value[count], count, 0, 1)
            else:
                print('Error en la cámara')
            count = count + 1
            line = red_line.pop(0)
            line.remove()
            line = red_line2.pop(0)
            line.remove()
    #_simplesound.save_invert_freq_sound(wav_path, alldata['hjd'], y_norm['mag'])
    _simplesound.save_filebisound(wav_path)

if starType == 'CGCas':
    ax.set_title('CG-Cas-Cepheid Camera bd')
    ax2.set_title('CG-Cas-Cepheid Camera bc')
    ax.scatter(bd_toplot['hjd'], bd_toplot['mag'], marker='.', c='#CF3476', label='bd')
    ax2.scatter(bc_toplot['hjd'], bc_toplot['mag'], marker='.', c='#E59866', label='bc')
    plot_path = 'data/galaxy-stars/light-curves/Cefeida/CGCas/cepheid_sonouno.png'
    wav_path = 'data/galaxy-stars/light-curves/Cefeida/CGCas/cepheid_sonouno.wav'
    reproduction(bd_toplot, bc_toplot, 'bd', 'bc', wav_path)
    
elif starType == 'RWPhe':
    ax.set_title('RW-Phe-Eclipsing Binary')
    ax.scatter(be_toplot['hjd'], be_toplot['mag'], marker='.', c='k', label='be')
    ax.scatter(bf_toplot['hjd'], bf_toplot['mag'], marker='.', c='g', label='bf')
    plot_path = 'data/galaxy-stars/light-curves/BEclipsante/RWPhe/eclipsante_sonouno.png'
    wav_path = 'data/galaxy-stars/light-curves/BEclipsante/RWPhe/eclipsante_sonouno.wav'
    reproduction(be_toplot, bf_toplot, 'be', 'bf', wav_path)

elif starType == 'V0748Cep':
    ax.set_title('V0748-Cep-Eclipsing Binary')
elif starType == 'ZLep':
    ax.set_title('Z-Lep-Eclipsing Binary')
elif starType == 'MNCam':
    ax.set_title('MN-Cam-Cepheid')
elif starType == 'HWPup':
    ax.set_title('HW-Pup-Cepheid')
else:
    ax.set_title(' ')

ax.legend() 
ax2.legend()    
# Save the plot
fig.savefig(plot_path)

rep=False
if rep:
    plt.pause(0.5)
    # Showing the above plot
    plt.show()
    plt.close()