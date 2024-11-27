#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os

from scipy.fftpack import fft


# fixed seed for reproducibility
np.random.seed(42)

# path to current test directory
tst_path      = os.path.realpath(__file__)
tst_path      = tst_path[:tst_path.find("python")]

# script settings
en_plots      = True
en_filegen    = False

# generated file path and names
fpath         = os.path.join(tst_path, 'cfg', 'default')
input_fnm     = "in.c"
output_fnm    = "out.c"
header_fnm    = "data.h"
# C array names
input_arr_nm  = "input"
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


def fwrite_header(fname, N, ifft_flag, snr_ref, input_arr_nm, output_arr_nm):
  outdir, f = os.path.split(fname)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with open(fname, 'w') as f:
    f.write("\n#ifndef DATA_H\n#define DATA_H\n")
    f.write("\n#include \"arm_math.h\"\n")
    f.write("\n")
    f.write("#define FFT_SIZE        ({:d})\n".format(N))
    f.write("#define IFFT_FLAG       ({:d})\n".format(ifft_flag))
    f.write("#define SNR_REF_THLD    ({:d})\n".format(snr_ref))
    f.write("\n")
    f.write("extern float32_t {:}[FFT_SIZE];\n".format(input_arr_nm))
    f.write("extern float32_t {:}[FFT_SIZE];\n".format(output_arr_nm))
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


def repack_cmsis_rfft(X, N):
  nyq = (N//2)
  X_re = np.real(X)
  X_im = np.imag(X)

  X_dc = X_re[0]
  X_nyq = X_re[nyq]

  X_cmsis = [X_dc, X_nyq]
  for i in range(1, nyq):
    X_cmsis += [X_re[i], X_im[i]]

  return np.array(X_cmsis)


""" FFT Design """
N  = 2048         # FFT size
ifft_flag = False # IFFT not currently supported by this script


""" Input Stimulus """
fs = 48000                        # sample frequency
n = np.arange(N)                  # sample indices
t = n / fs                        # discrete time
freq = n / (N/fs)                 # discrete frequency

tone_freq_hz = [100, 4000, 8000]  # input tones
tone_amp_dB  = [-30, -20, -10]    # input tone powers
en_noise = True                   # optionally include zero-mean, unit std WGN
noise_dB = -20                    # noise power

# generate and sum up the pure tones
x_pure = (np.power(10,(tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)
for i in range(1, len(tone_freq_hz)):
  x_pure += (np.power(10,(tone_amp_dB[i]/20))) * np.sin(2 * np.pi * tone_freq_hz[i] * t)

# optionally add zero-mean gaussian white noise
if en_noise:
  x = x_pure + (np.power(10, (noise_dB/20)) * np.random.normal(0, 1, N))
else:
  x = x_pure

# print(len(x), type(x))


""" FFT output """
X = fft(x=x, n=N)


""" Pack the FFT output according to the CMSIS spec """
X_cmsis = repack_cmsis_rfft(X, N)


""" Calculate the expected SNR of 32b precision result """
x_32b = x.astype(np.float32)
X_32b = fft(x=x_32b, n=N)
X_32b_cmsis = repack_cmsis_rfft(X_32b, N)
snr = snr_32b(X_cmsis, X_32b_cmsis)
# the cmsis implementation seems to introduce some small extra loss of precision
snr_ref = int(snr) - 1


""" Plot """
if en_plots:
  nyq = (N//2)
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

  plt.subplot(122)
  # spectrum is symmetric for real input, so only plot the first half
  plt.stem(freq[:nyq+1], np.abs(X[:nyq+1]), 'b', markerfmt=" ", basefmt="-b")
  plt.xlabel('frequency (Hz)')
  plt.ylabel('|X(freq)|')
  plt.title('Spectrum')

  plt.tight_layout()
  plt.show()


""" Write to files """
if en_filegen:
  fname = os.path.join(fpath, input_fnm)
  fwrite_array_f32(fname, arr_name=input_arr_nm, arr_size='FFT_SIZE', arr=x, per_line=8)

  fname = os.path.join(fpath, output_fnm)
  fwrite_array_f32(fname, arr_name=output_arr_nm, arr_size='FFT_SIZE', arr=X_cmsis, per_line=8)

  fname = os.path.join(fpath, header_fnm)
  fwrite_header(fname, N, ifft_flag, snr_ref, input_arr_nm, output_arr_nm)
