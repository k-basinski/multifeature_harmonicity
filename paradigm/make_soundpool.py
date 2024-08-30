import numpy as np
import inharmonicon as inharm
from progress.bar import Bar

# stimulus length in seconds
stim_length = .07

# jitter rate for inharmonic sounds
jr = 0.1

# how many inharmonic sounds in pool?
no_inharmonic_sounds = 1000

# filepath to save output
fpath = 'sound_pool_multifeature/'

# make harmonic sounds
print("Generating harmonic sounds...")

# make harmonic series
hs_std, hs_dev_pos, hs_dev_neg = (inharm.Harmonics(500),
                                  inharm.Harmonics(550),
                                  inharm.Harmonics(450)
                                  )

# generate standard
harm_std = inharm.Sound(f=hs_std, length=stim_length)
harm_std.save(fpath + 'harm_std.wav')

# pitch oddballs
harm_pitch_pos = inharm.Sound(f=hs_dev_pos, length=stim_length)
harm_pitch_pos.save(fpath + 'harm_pitch_pos.wav')

harm_pitch_neg = inharm.Sound(f=hs_dev_neg, length=stim_length)
harm_pitch_neg.save(fpath + 'harm_pitch_neg.wav')

# intensity oddballs
harm_int_pos = inharm.Sound(f=hs_std, length=stim_length)
harm_int_pos.adjust_volume(+10)
harm_int_pos.save(fpath + 'harm_pitch_pos.wav')

harm_int_neg = inharm.Sound(f=hs_std, length=stim_length)
harm_int_neg.adjust_volume(-10)
harm_int_neg.save(fpath + 'harm_int_neg.wav')

# location oddballs
harm_loc_pos = inharm.Sound(f=hs_std, length=stim_length)
harm_loc_pos.apply_itd(800, 'right')
harm_loc_pos.save(fpath + 'harm_loc_pos.wav')

harm_loc_neg = inharm.Sound(f=hs_std, length=stim_length)
harm_loc_neg.apply_itd(800, 'left')
harm_loc_neg.save(fpath + 'harm_loc_neg.wav')

# omission oddball
harm_omission = inharm.Sound(None, length=stim_length)
harm_omission.save(fpath + 'omission.wav')


# make inharmonic sounds
print(f"Generating {no_inharmonic_sounds} sounds...")
for i in  Bar('Processing').iter(range(no_inharmonic_sounds)):
    # inharmonic series
    series_std = inharm.Harmonics(500, jitter_rate=jr)
    jit_factors = series_std.get_factors()
    series_dev_pos = inharm.Harmonics(550, jitter_factors=jit_factors, fmax=len(jit_factors))
    series_dev_neg = inharm.Harmonics(450, jitter_factors=jit_factors, fmax=len(jit_factors))

    # inharmonic standard
    son = inharm.Sound(series_std, length=stim_length)
    son.save(f'{fpath}ih_std_{i}.wav')

    # pitch deviants
    son = inharm.Sound(series_dev_pos, length=stim_length)
    son.save(f'{fpath}ih_pitch_pos_{i}.wav')
    son = inharm.Sound(series_dev_neg, length=stim_length)
    son.save(f'{fpath}ih_pitch_neg_{i}.wav')

    # intensity deviants
    son = inharm.Sound(series_std, length=stim_length)
    son.adjust_volume(+10)
    son.save(f'{fpath}ih_int_pos_{i}.wav')
    son.adjust_volume(-20)
    son.save(f'{fpath}ih_int_neg_{i}.wav')

    # location deviants
    son = inharm.Sound(series_std, length=stim_length)
    son.apply_itd(800, 'right')
    son.save(f'{fpath}ih_loc_pos_{i}.wav')
    son = inharm.Sound(series_std, length=stim_length)
    son.apply_itd(800, 'left')
    son.save(f'{fpath}ih_loc_neg_{i}.wav')



