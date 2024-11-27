#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os

from scipy import signal

# USER: select number of samples
#   desired clean output signal length (beyond initial noisy output)
N             = 128

# USER: script settings
en_plots      = False
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


def fwrite_header(fname, n_sos, t_samples, n_samples, snr_ref, input_arr_nm, output_arr_nm, coeff_arr_nm):
  outdir, f = os.path.split(fname)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with open(fname, 'w') as f:
    f.write("\n#ifndef DATA_H\n#define DATA_H\n")
    f.write("\n#include \"arm_math.h\"\n")
    f.write("\n")
    f.write("#define N_STAGES        ({:d})\n".format(n_sos))
    f.write("#define TOTAL_SAMPLES   ({:d})\n".format(t_samples))
    f.write("#define N_SAMPLES       ({:d})\n".format(n_samples))
    f.write("#define N_INITIAL       ({:d})\n".format(t_samples-n_samples))
    f.write("#define SNR_REF_THLD    ({:d})\n".format(snr_ref))
    f.write("\n")
    f.write("extern float32_t {:}[N_STAGES*5];\n".format(coeff_arr_nm))
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


# def snr(tst, ref):
#   sz = min(len(tst), len(ref))
#   energy_tst = np.sum(tst * tst)
#   energy_err = np.sum((ref - tst) * (ref - tst))
#   snr = 10 * np.log10(energy_tst / energy_err)
#   return snr


def moving_average(a, n=3):
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n


""" Filter Design """
order = 6          # IIR filter order
n_sos = order//2   # number of second-order stages
fs    = 48000      # sample frequency (Hz)
ftype = 'butter'   # filter type
btype = 'lowpass'  # filter type
fc    = 1000       # cutoff frequency (Hz)

sos = signal.iirfilter(N=order, Wn=fc, btype=btype, analog=False, ftype=ftype, output='sos', fs=fs)

# print(len(sos), type(sos))
# print(sos)


""" Input Stimulus """
N_long = 1024                     # starting signal length

n = np.arange(N_long)             # sample indices
t = n / fs                        # discrete time

tone_freq_hz = [100, 4000, 8000]  # input tones
tone_amp_dB  = [-30, -20, -10]    # input tone powers
en_noise = False                  # optionally include zero-mean, unit std WGN
noise_dB = -20                    # noise power

# generate and sum up the pure tones
x_pure = (np.power(10,(tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)
for i in range(1, len(tone_freq_hz)):
  x_pure += (np.power(10,(tone_amp_dB[i]/20))) * np.sin(2 * np.pi * tone_freq_hz[i] * t)

# optionally add zero-mean gaussian white noise
if en_noise:
  x = x_pure + (np.power(10, (noise_dB/20)) * np.random.normal(0, 1, N_long))
else:
  x = x_pure

# print(len(x), type(x))


""" Filtered Output """
# The filter function is implemented as a series of second-order filters with direct-form II transposed structure.
y = signal.sosfilt(sos, x)
# print(len(y), type(y))

# approximate phase delay for 100 hz tone output
x_100hz = (np.power(10,(tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)
correlation = signal.correlate(y, x_100hz, mode="full")
lags = signal.correlation_lags(y.size, x_100hz.size, mode="full")
delay = lags[np.argmax(correlation)]

# ignore noisy output from initial conditions
diff = np.abs(y[delay:] - x_100hz[:-delay])
diff = moving_average(diff, n=32)
N_initial = np.where(diff < 0.00015)[0][0]


""" Pack SOS according to the CMSIS spec """
# each row is [b0, b1, b2, a0, a1, a2]
# make sure that a0 = 1 (divide each row by a0)
coeff = sos / sos[:,3].reshape(3,1)
# remove the a0 column and flip the signs of a1 and a2
coeff = np.hstack((coeff[:,:3], -coeff[:,4:]))
# remove the total gain from the first section
# and distribute it across all sections
total_gain = coeff[0,0]
sec_gain = np.power(total_gain, 1/n_sos)
coeff[0,:3] = coeff[0,:3] / total_gain
coeff[:,:3] = coeff[:,:3] * sec_gain
# flatten the array (# stages * 5 coeffs per stage)
coeff = np.reshape(coeff, n_sos*5)


""" Calculate the expected SNR of 32b precision result """
x_32b = x.astype(np.float32)
sos_32b = sos.astype(np.float32)
y_32b = signal.sosfilt(sos_32b, x_32b)
snr = snr_32b(y, y_32b)
# the cmsis implementation seems to introduce some small extra loss of precision
snr_ref = int(snr) - 5


""" Plot """
if en_plots:
  delay_t = delay / fs

  plt.figure(figsize = (12, 6))
  plt.subplot(121)
  plt.plot(n, x)  # original signal
  plt.plot(n, y, 'r')  # filtered
  plt.xlabel('sample')
  plt.ylabel('amplitude')
  plt.legend(['x', 'y'])
  plt.title('Input and Output')

  # Plot the good part of the filtered signal vs a pure 100hz tone
  plt.subplot(122)
  plt.plot(t, x_100hz)  # pure 100hz tone
  plt.plot(t[N_initial:]-delay_t, y[N_initial:], 'r')  # the "good" part of the filtered signal
  plt.xlabel('time')
  plt.ylabel('amplitude')
  plt.legend(['pure tone', 'y (good part)'])
  plt.title('Filter Ouput vs Pure Tone')

  plt.show()


""" Write to file """
if en_filegen:
  input = x[:N_initial + N]
  output_ref = y[N_initial:N_initial + N]

  fpath         = os.path.join(fpath, 'sos{:}_n{:}'.format(n_sos, N))

  fname = os.path.join(fpath, coeff_fnm)
  fwrite_array_f32(fname, arr_name=coeff_arr_nm, arr=coeff, arr_size='N_STAGES*5', per_line=8)

  fname = os.path.join(fpath, output_fnm)
  fwrite_array_f32(fname, arr_name=output_arr_nm, arr=output_ref, arr_size='N_SAMPLES', per_line=8)

  fname = os.path.join(fpath, input_fnm)
  fwrite_array_f32(fname, arr_name=input_arr_nm, arr=input, arr_size='TOTAL_SAMPLES', per_line=8)

  fname = os.path.join(fpath, header_fnm)
  fwrite_header(fname, snr_ref=snr_ref, n_sos=n_sos,
                t_samples=(N+N_initial), n_samples=N,
                input_arr_nm=input_arr_nm, output_arr_nm=output_arr_nm, coeff_arr_nm=coeff_arr_nm)
