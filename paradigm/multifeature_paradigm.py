#####################################
####### MultiFeature Oddball ########
#####################################
#####################################

# harm, ih - harmoniczne, nieharmoniczne
# int,pitch,loc - głośność, pitch, lokalizacja
# omission - omission
# nieharmonicznych jest po 1000 z każdego

# imports
from psychopy import visual, core, prefs, visual, sound, event, gui, logging
from psychopy.hardware import keyboard
prefs.hardware["audioLib"] = ["PTB"]
prefs.hardware["audioLatencyMode"] = 4


import serial

import numpy as np


# Config
send_triggers = False
pool_dir = 'soundpool'
logging = True
ioi = .6 # interonset interval in seconds
full_screen = True

# get subject info:
ID_box = gui.Dlg(title="Subject identity")
ID_box.addField("ID: ")
sub_id = ID_box.show()
ID_box.show()

# create a window
color = "white"
win = visual.Window([800, 600], color="black", fullscr=full_screen)

window_elements = {}

blocks = np.array([
    "harmonic",
    "inharmonic",
    "changing",
    "in_deviants"
])
# shuffle blocks for randomization
np.random.shuffle(blocks)

if send_triggers:
    port = serial.Serial("/dev/tty.usbserial-D30C1INU", 115200)
    
# %%
# sound pool musi byc na setcie unikalnych dzwiekow dla danej sekwencji, zeby psychopy na zadnym etapie nie musial ladowac wszystkich dzwiekow z folderu

def populate_sound_pool(sound_list):
    sound_list = set(sound_list)
    sound_pool = {}
    for s in sound_list:
        sound_pool[s] = sound.Sound(f"{pool_dir}/{s}.wav", hamming=False)

    print("Loading sound pool done. Press any key...")
    kb = keyboard.Keyboard()
    while True:
        win.flip()
        if len(kb.getKeys()) > 0:
            break
    return sound_pool


# def make_sound_list(jit, patterns):
#     sound_list = []

#     for pattern in patterns:
#         for stddev in ['std', 'dev']:
#             tag = f'{stddev}_{pattern}_{jit}'
#             sound_list.append(tag)

#     return sound_list

def send_trigger(port, value):
    """
    Send a trigger to the port.

    Parameters:
    port (object): The port object to send the trigger to.
    value (int): The value to send to the port.

    Returns:
    None
    """
    # make sure value is integer
    value_int = int(value)
    trig = value_int.to_bytes(1, "big")
    win.callOnFlip(port.write, trig)

def concatenate_integers(a, b):
    return int(f"{a}{b}") #could be also aritmetic solution that is a*10+b

def calculate_stim_count(block_length: int, ioi: float): 
    """
    Calculate the number of stimuli that can fit in a block.

    This function calculates the number of stimuli that can fit in a block
    based on the block length and the inter-onset interval (IOI).

    Parameters:
        block_length (int): The length of the block in seconds.
        ioi (float): The inter-onset interval in seconds.

    Returns:
        int: The number of stimuli that can fit in the block.
    """
    from math import floor
    s_count = floor(block_length / ioi) 
    return s_count

def calculate_interonset_frames(ioi: float):
    """Get number of frames to flip for a given IOI.
    """
    return int(120 * ioi) - 1


def play_sound_from_dict(stim_list: list, sound_pool: dict, block_id):
    """
    Play sounds from a list of stimuli using a dictionary of sounds.

    Parameters:
        stim_list (list): A list of stimuli to be played.
        sound_pool (dict): A dictionary of sounds,
            where the keys are the stimulus types
            and the values are the sound objects.

    Returns:
        None
    """
    list_length = len(stim_list)
    count = 1
    for stim in stim_list:
        if stim in sound_pool:
            play_sound(sound_pool[stim])
            #trigger = trigger_pool[stim] + add_to_trigger # add_to_trigger = 0 parameter
            trigger = concatenate_integers(trigger_pool[stim], block_id) 
            if send_triggers:
                send_trigger(port, trigger)
            flip_screen(1, window_elements)

            if logging:
                msg_text = f'Block {block}, sound {count}/{list_length}. Played {stim}, triggered {trigger}.'
                window_elements['message1'] = visual.TextStim(win, pos=[0,0],text=msg_text)
                print(msg_text)

            count += 1

            flip_screen(calculate_interonset_frames(ioi), window_elements)

        else:
            print(f"Unknown stimulus: {stim}")


def play_sound(sound: object):
    """
    This function plays a sound from a sound pool on the next flip.
    It takes a sound object as input and uses the `win.getFutureFlipTime()` function
    to determine the next flip time. The sound is then
    played using the `sound.play()` method.

    Parameters:
    sound (object): The sound object to play.

    Returns:
    None
    """
    next_flip = win.getFutureFlipTime(clock="ptb")
    sound.play(when=next_flip)


def flip_screen(times: int = 1, window_elements=None):
    """
    Flips the screen a specified number of times.

    Parameters:
        times (int): The number of times to flip the screen. Default is 1.
        window_elements (dict): A dictionary of window objects to show.
    """
    for _ in range(times):
        for _, v in window_elements.items():
            v.draw()
        win.flip()


def quit_exp():
    win.close()
    # logging.flush()
    core.quit()


def insert_cross():
    stname_screen = visual.TextStim(win, text="+", color="white", height=0.2)
    stname_screen.draw()

# create quit key:
event.globalKeys.add(key="escape", func=quit_exp, name="shutdown")
keyNext = "space"


############### SEQS #################

rng = np.random.default_rng()

def make_harmonic_seq():
    rng = np.random.default_rng()
    standards = 'harm_std'
    deviants = [
        rng.choice(['harm_pitch_neg', 'harm_pitch_pos']),
        rng.choice(['harm_loc_neg', 'harm_loc_pos']),
        rng.choice(['harm_int_neg', 'harm_int_pos']),
        'omission',
        f'ih_std_{rng.integers(0, 1000)}'
    ]
    
    deviant_order = np.random.choice(deviants, 5, replace=False)
    
    sequence = []
    for i in range(5):
        sequence.append(standards)
        sequence.append(deviant_order[i])
      
        
    return sequence

def make_inharmonic_seq(ih_id):
    rng = np.random.default_rng()
    standards = f'ih_std_{ih_id}'
    deviants = [
        rng.choice([f'ih_pitch_neg_{ih_id}', f'ih_pitch_pos_{ih_id}']),
        rng.choice([f'ih_loc_neg_{ih_id}', f'ih_loc_pos_{ih_id}']),
        rng.choice([f'ih_int_neg_{ih_id}', f'ih_int_pos_{ih_id}']),
        'omission',
        'harm_std'
    ]
    
    deviant_order = np.random.choice(deviants, 5, replace=False)
    
    sequence = []
    for i in range(5):
        sequence.append(standards)
        sequence.append(deviant_order[i])
        
        
    return sequence


def make_changing_seq():
    rng = np.random.default_rng()
    randints = rng.integers(0, 1000, 8)
    standards = [f'ih_std_{randints[i]}' for i in range(5)]
    
    deviants = [
        rng.choice([f'ih_pitch_neg_{randints[5]}', f'ih_pitch_pos_{randints[5]}']),
        rng.choice([f'ih_loc_neg_{randints[6]}', f'ih_loc_pos_{randints[6]}']),
        rng.choice([f'ih_int_neg_{randints[7]}', f'ih_int_pos_{randints[7]}']),
        'omission',
        'harm_std'
    ]
    
    deviant_order = np.random.choice(deviants, 5, replace=False)
    
    sequence = []
    for i in range(5):
        sequence.append(standards[i])
        sequence.append(deviant_order[i])
        
    return sequence


def make_inharmonic_deviants():
    rng = np.random.default_rng()
    randints = rng.integers(0, 1000, 3)
    standards = 'harm_std'
    deviants = [
        rng.choice([f'ih_pitch_neg_{randints[0]}', f'ih_pitch_pos_{randints[0]}']),
        rng.choice([f'ih_loc_neg_{randints[1]}', f'ih_loc_pos_{randints[1]}']),
        rng.choice([f'ih_int_neg_{randints[2]}', f'ih_int_pos_{randints[2]}'])
    ]
    
    deviant_order = np.random.choice(deviants, 3, replace=False)
    
    sequence = []
    for i in range(3):
        sequence.append(standards)
        sequence.append(deviant_order[i])
        
    return sequence  


# %%

# make a trigger pool
trigger_pool = {}

trigger_pool['harm_std'] = 1
trigger_pool['harm_int_pos'] = 2
trigger_pool['harm_int_neg'] = 3
trigger_pool['harm_loc_pos'] = 4
trigger_pool['harm_loc_neg'] = 5
trigger_pool['harm_pitch_pos'] = 6
trigger_pool['harm_pitch_neg'] = 7
trigger_pool['omission'] = 8
for i in range(1000):
    trigger_pool[f'ih_std_{i}'] = 11
    trigger_pool[f'ih_int_pos_{i}'] = 12
    trigger_pool[f'ih_int_neg_{i}'] = 13
    trigger_pool[f'ih_loc_pos_{i}'] = 14
    trigger_pool[f'ih_loc_neg_{i}'] = 15
    trigger_pool[f'ih_pitch_pos_{i}'] = 16
    trigger_pool[f'ih_pitch_neg_{i}'] = 17


# %%
rng = np.random.default_rng()
seq_harm = []
seq_inharm = []
seq_changing = []
seq_inharm_dev = []
total_sounds = 600
num_sequences = total_sounds // 10            
for _ in range(num_sequences):
    seq_harm += make_harmonic_seq()
    seq_inharm += make_inharmonic_seq(rng.integers(0,1000))
    seq_changing += make_changing_seq()
    seq_inharm_dev += make_inharmonic_deviants()
    
# %%

for block in blocks:
    # Harmonic
    if block == "harmonic":
        sound_list = seq_harm
        sp = populate_sound_pool(sound_list)
        sl = seq_harm
        play_sound_from_dict(sl, sp, block_id=1)

    # Inharmonic
    elif block == "inharmonic":
        sound_list = seq_inharm
        sp = populate_sound_pool(sound_list)
        sl = seq_inharm
        play_sound_from_dict(sl, sp, block_id=2)
        
    elif block == "changing":
        sound_list = seq_changing
        sp = populate_sound_pool(sound_list)
        sl = seq_changing
        play_sound_from_dict(sl, sp, block_id=3)
        
    elif block == "in_deviants":
        sound_list = seq_inharm_dev
        sp = populate_sound_pool(sound_list)
        sl = seq_inharm_dev
        play_sound_from_dict(sl, sp, block_id=4)
    
    # finally, delete sound pool
    del sp, sl
    
print('Done and done!')
quit_exp()