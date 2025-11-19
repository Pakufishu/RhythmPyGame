import os
from variables import *

song_folder = [f for f in os.listdir(SONGS_FOLDER)]
def getsongdict():
    songsdic = {}
    for name in song_folder:
        name_files = os.path.join(SONGS_FOLDER, name)
        songdic = {}
        for f in os.listdir(name_files):
            songdic['name'] = name
            if f.lower().endswith(".json"):
                songdic['settings'] = os.path.join(name_files, f)
            if f.endswith('Ez.txt'):
                songdic['Ez'] = os.path.join(name_files, f)
            if f.endswith('Adv.txt'):
                songdic['Adv'] =  os.path.join(name_files, f)
            if f.endswith('Exp.txt'):
                songdic['Exp'] = os.path.join(name_files, f)
            if f.endswith('Mas.txt'):
                songdic['Mas'] = os.path.join(name_files, f)
            if f.endswith('.wav'):
                songdic['Music'] = os.path.join(name_files, f)
            if f.lower().endswith('bg.png'):
                songdic['Bg'] = os.path.join(name_files, f)
            if f.lower().endswith('art.png'):
                songdic['Art'] = os.path.join(name_files, f)
        songsdic[name] = songdic
    return songsdic