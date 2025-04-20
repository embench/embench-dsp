#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os

from scipy import signal


# USER: select number of samples
#   desired clean output signal length (beyond initial noisy output)
N             = 128

# USER: script settings
en_plots      = True
en_filegen    = False


# fixed seed for reproducibility
np.random.seed(42)

# path to current test directory
tst_path      = os.path.realpath(__file__)
tst_path      = tst_path[:tst_path.find("python")]

# generated file path and names
fpath         = os.path.join(tst_path, 'cfg')
input_fnm     = "in.c"
output_fnm    = "out.c"
coeff_fnm     = "coeff.c"
header_fnm    = "data.h"
# C array names
input_arr_nm  = "input"
coeff_arr_nm  = "coeff"
output_arr_nm = "output_ref"


def fwrite_array_f32(fname, arr_name, arr_size, arr, per_line):
  """ Write array to C file """
  outdir, f = os.path.split(fname)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  float_fmt = '{:13.10f}'  # 13 digits total, 10 decimal points floating-point
  sz = len(arr)
  with open(fname, 'w') as f:
    f.write("\n#include \"data.h\"")
    f.write("\n\nfloat32_t {:}[{:}] = \n{{\n  ".format(arr_name, arr_size))
    for i in range(sz):
      if i == (sz - 1):
        f.write("{:}f\n".format(float_fmt.format(arr[i])))
      else:
        f.write("{:}f, ".format(float_fmt.format(arr[i])))
        if ((i+1) % per_line) == 0:
          f.write("\n  ")
    f.write("};\n")


def fwrite_header(fname, n_taps, t_samples, n_samples, snr_ref, input_arr_nm, output_arr_nm, coeff_arr_nm):
  outdir, f = os.path.split(fname)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with open(fname, 'w') as f:
    f.write("\n#ifndef DATA_H\n#define DATA_H\n")
    f.write("\n#include \"arm_math.h\"\n")
    f.write("\n")
    f.write("#define N_TAPS          ({:d})\n".format(n_taps))
    f.write("#define TOTAL_SAMPLES   ({:d})\n".format(t_samples))
    # f.write("#define N_INITIAL       ({:d})\n".format(n_initial))
    f.write("#define N_SAMPLES       ({:d})\n".format(n_samples))
    f.write("#define SNR_REF_THLD    ({:d})\n".format(snr_ref))
    f.write("\n")
    f.write("extern float32_t {:}[N_TAPS];\n".format(coeff_arr_nm))
    f.write("extern float32_t {:}[TOTAL_SAMPLES];\n".format(input_arr_nm))
    f.write("extern float32_t {:}[N_SAMPLES];\n".format(output_arr_nm))
    f.write("\n#endif  // DATA_H\n")


def snr_32b(ref, tst):
  """ Calculate the SNR in 32-bit floating-point precision. """
  energy_sig = np.float32(0)
  energy_err = np.float32(0)
  ref_32b = ref.astype(np.float32)
  tst_32b = tst.astype(np.float32)
  for ri, ti in zip(ref_32b, tst_32b):
    energy_sig += np.power(ri, np.float32(2))
    energy_err += np.power(np.subtract(ri, ti), np.float32(2))
  snr = np.float32(10) * np.log10(np.divide(energy_sig, energy_err))
  return snr


""" Filter Design """
n_taps = 256        # FIR filter order
fs     = 48000      # sample frequency (Hz)
win    = "hamming"  # filter window type
fc     = 1000       # cutoff frequency
scale  = True       # sampling flag

coeff = signal.firwin(n_taps, fc, window=win, scale=scale, fs=fs)
# print(len(coeff), type(coeff))
# print(coeff)


""" Input Stimulus """
N_tot = n_taps + N                # signal length

n = np.arange(N_tot)              # sample indices
t = n / fs                        # discrete time

tone_freq_hz = [100, 4000, 8000]  # input tones
tone_amp_dB  = [-10, -20, -10]    # input tone powers
en_noise = True                   # optionally include zero-mean, unit std WGN
noise_dB = -30                    # noise power

# generate and sum up the pure tones
x_pure = (np.power(10,(tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)
for i in range(1, len(tone_freq_hz)):
  x_pure += (np.power(10,(tone_amp_dB[i]/20))) * np.sin(2 * np.pi * tone_freq_hz[i] * t)

# optionally add zero-mean gaussian white noise
if en_noise:
  x = x_pure + (np.power(10, (noise_dB/20)) * np.random.normal(0, 1, N_tot))
else:
  x = x_pure

# print(len(x), type(x))


""" Filtered Output """
y = signal.lfilter(coeff, 1.0, x)
# print(len(y), type(y))


""" Calculate the expected SNR of 32b precision result """
x_32b = x.astype(np.float32)
coeff_32b = coeff.astype(np.float32)
y_32b = signal.lfilter(coeff_32b, np.float32(1.0), x_32b)
snr = snr_32b(y, y_32b)
# the cmsis implementation seems to introduce some extra loss of precision
snr_ref = int(snr) - 20


""" Plot """
if en_plots:
  # The phase delay of the filtered signal. The first n_taps-1
  # samples are "corrupted" by the initial conditions
  delay = 0.5 * (n_taps-1) / fs

  plt.figure(figsize = (12, 6))
  plt.subplot(121)
  plt.plot(n, x)  # original signal
  plt.plot(n, y, 'r')  # filtered
  plt.xlabel('sample')
  plt.ylabel('amplitude')
  plt.legend(['x', 'y'])
  plt.title('Input and Output')

  # plt.figure(2)
  # plt.plot(t, x)  # original signal
  # plt.plot(t[n_taps-1:]-delay, y[n_taps-1:], 'r')  # the "good" part of the filtered signal
  # plt.xlabel('time')
  # plt.legend(['x', 'filtered x (good part)'])

  # Plot the good part of the filtered signal vs a pure 100hz tone
  x_100hz = (np.power(10,(tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)
  plt.subplot(122)
  plt.plot(t, x_100hz)  # pure 100hz tone
  plt.plot(t[n_taps-1:]-delay, y[n_taps-1:], 'r')  # the "good" part of the filtered signal
  plt.xlabel('time')
  plt.ylabel('amplitude')
  plt.legend(['pure tone', 'y (good part)'])
  plt.title('Filter Ouput vs Pure Tone')

  plt.show()


""" Write to file """
if en_filegen:
  fpath         = os.path.join(fpath, 'taps{:}_n{:}'.format(n_taps, N))

  fname = os.path.join(fpath, coeff_fnm)
  fwrite_array_f32(fname, arr_name=coeff_arr_nm, arr=coeff, arr_size='N_TAPS', per_line=8)

  fname = os.path.join(fpath, output_fnm)
  fwrite_array_f32(fname, arr_name=output_arr_nm, arr=y[n_taps:], arr_size='N_SAMPLES', per_line=8)

  fname = os.path.join(fpath, input_fnm)
  fwrite_array_f32(fname, arr_name=input_arr_nm, arr=x, arr_size='TOTAL_SAMPLES', per_line=8)

  fname = os.path.join(fpath, header_fnm)
  fwrite_header(fname, n_taps=n_taps,
                t_samples=N_tot, n_samples=N,
                snr_ref=snr_ref,
                input_arr_nm=input_arr_nm, output_arr_nm=output_arr_nm, coeff_arr_nm=coeff_arr_nm)
