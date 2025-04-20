#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os

from scipy.fftpack import dct


# USER: script settings
en_plots      = True
en_filegen    = False


# fixed seed for reproducibility
np.random.seed(42)

# path to current test directory
tst_path      = os.path.realpath(__file__)
tst_path      = tst_path[:tst_path.find("python")]

# generated file path and names
fpath         = os.path.join(tst_path, 'cfg', 'default')
input_fnm     = "in.c"
output_fnm    = "out.c"
header_fnm    = "data.h"
# C array names
input_arr_nm  = "inout"
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


def fwrite_header(fname, dct_size, snr_ref, input_arr_nm, output_arr_nm):
  outdir, f = os.path.split(fname)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with open(fname, 'w') as f:
    f.write("\n#ifndef DATA_H\n#define DATA_H\n")
    f.write("\n#include \"arm_math.h\"\n")
    f.write("\n")
    f.write("#define DCT4_SIZE       ({:d})\n".format(dct_size))
    f.write("#define SNR_REF_THLD    ({:d})\n".format(snr_ref))
    f.write("\n")
    f.write("extern float32_t {:}[DCT4_SIZE];\n".format(input_arr_nm))
    f.write("extern float32_t {:}[DCT4_SIZE];\n".format(output_arr_nm))
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


""" DCT Design """
dct_size = 512     # DCT size


""" Input Stimulus """
fs   = 48000                      # sample frequency (Hz)
n    = np.arange(dct_size)        # sample indices
t    = n / fs                     # discrete time
freq = (0.5*n / (dct_size/fs))    # discrete frequency

tone_freq_hz = [100, 4000, 8000]  # input tones
tone_amp_dB  = [-30, -20, -10]    # input tone powers
en_noise = True                   # optionally include zero-mean, unit std WGN
noise_dB = -25                    # noise power

# generate and sum up the pure tones
x_pure = (np.power(10,(tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)
for i in range(1, len(tone_freq_hz)):
  x_pure += (np.power(10,(tone_amp_dB[i]/20))) * np.sin(2 * np.pi * tone_freq_hz[i] * t)

# optionally add zero-mean gaussian white noise
if en_noise:
  x = x_pure + (np.power(10, (noise_dB/20)) * np.random.normal(0, 1, dct_size))
else:
  x = x_pure

# print(len(x), type(x))


""" DCT Output """
X = dct(x=x, type=4, n=dct_size, norm="ortho")

# print(X, len(X))



""" Calculate the expected SNR of 32b precision result """
x_32b = x.astype(np.float32)
X_32b = dct(x=x_32b, type=4, n=dct_size, norm="ortho")
snr = snr_32b(X, X_32b)
# the cmsis implementation seems to introduce extra loss of precision
snr_ref = int(snr) - 20


""" Plot """
if en_plots:
  nyq = (dct_size//2)
  plt.figure(figsize = (12, 6))
  plt.subplot(121)
  if en_noise:
    plt.plot(n, x_pure) # original signal
    plt.plot(n, x)      # noisy signal
    plt.legend(["x (original)", "x (noisy)"])
  else:
    plt.plot(n, x)
    plt.legend(["x"])
  plt.xlabel('sample')
  plt.ylabel('amplitude')
  plt.title('Input')

  # Plot the good part of the filtered signal vs a pure 100hz tone
  plt.subplot(122)
  plt.stem(freq, np.abs(X), 'b', markerfmt=" ", basefmt="-b")
  plt.xlabel('frequency (Hz)')
  plt.ylabel('|X(freq)|')
  plt.title('DCT Spectrum')

  plt.tight_layout()
  plt.show()


""" Write to file """
if en_filegen:
  fname = os.path.join(fpath, input_fnm)
  fwrite_array_f32(fname, arr_name=input_arr_nm, arr=x, arr_size='DCT4_SIZE', per_line=8)

  fname = os.path.join(fpath, output_fnm)
  fwrite_array_f32(fname, arr_name=output_arr_nm, arr=X, arr_size='DCT4_SIZE', per_line=8)

  fname = os.path.join(fpath, header_fnm)
  fwrite_header(fname, dct_size=dct_size, snr_ref=snr_ref, input_arr_nm=input_arr_nm, output_arr_nm=output_arr_nm)
