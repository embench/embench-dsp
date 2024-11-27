#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os

from padasip.filters import FilterLMS


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
ref_fnm       = "ref.c"
header_fnm    = "data.h"
# C array names
input_arr_nm  = "input"
ref_arr_nm    = "ref"
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


def fwrite_header(fname, n_taps, t_samples, n_samples, snr_ref, mu, input_arr_nm, output_arr_nm, ref_arr_nm):
  float_fmt = '{:13.10f}f'  # 13 digits total, 10 decimal points floating-point
  outdir, f = os.path.split(fname)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with open(fname, 'w') as f:
    f.write("\n#ifndef DATA_H\n#define DATA_H\n")
    f.write("\n#include \"arm_math.h\"\n")
    f.write("\n")
    f.write("#define N_TAPS          ({:d})\n".format(n_taps))
    f.write("#define TOTAL_SAMPLES   ({:d})\n".format(t_samples))
    f.write("#define N_SAMPLES       ({:d})\n".format(n_samples))
    f.write("#define SNR_REF_THLD    ({:d})\n".format(snr_ref))
    f.write("\n")
    f.write("#define N_INITIAL       (TOTAL_SAMPLES-N_SAMPLES)\n")
    f.write("\n")
    f.write("static float32_t mu = {:};\n".format(float_fmt.format(mu)))
    f.write("\n")
    f.write("extern float32_t {:}[TOTAL_SAMPLES];\n".format(input_arr_nm))
    f.write("extern float32_t {:}[TOTAL_SAMPLES];\n".format(ref_arr_nm))
    f.write("extern float32_t {:}[TOTAL_SAMPLES];\n".format(output_arr_nm))
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


""" Input Stimulus """
N_init = n_taps
N_tot = N_init + N                # signal length

n = np.arange(N_tot)              # sample indices
t = n / fs                        # discrete time

tone_freq_hz = [100, 4000, 8000]  # input tones
tone_amp_dB  = [-10, -20, -10]    # input tone powers
en_noise = False                   # optionally include zero-mean, unit std WGN
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

# design the system "filter" that we want our adaptive filter to model
#   --> we want it to act as a BPF, outputing only the second (4kHz) tone
y_ref = (np.power(10, (tone_amp_dB[0]/20))) * np.sin(2 * np.pi * tone_freq_hz[0] * t)

# arrange the input and output ref on a sample-by-sample basis, preserving the history
x_r = np.zeros((N_tot, n_taps))
y_r = np.reshape(y_ref, (N_tot,))
buff = np.zeros(n_taps)
for i in range(N_tot):
  buff[1:n_taps-1] = buff[0:n_taps-2]  # advance the delay buffer
  buff[0] = x[i]  # add the new sample
  x_r[i,:] = buff  # this frame becomes the next input to the LMS filter


""" Filtered Output """
mu = 0.05
f = FilterLMS(n=n_taps, mu=mu, w="zeros")
y, e, w = f.run(y_r, x_r)


""" Calculate the expected SNR of 32b precision result """
x_r_32b = x_r.astype(np.float32)
y_r_32b = y_r.astype(np.float32)
mu_32b = np.float32(mu)
f_32b = FilterLMS(n=n_taps, mu=mu_32b, w="zeros")
y_32b, e_32b, w_32b = f_32b.run(y_r_32b, x_r_32b)
snr = snr_32b(y, y_32b)
# the cmsis implementation seems to introduce some extra loss of precision
snr_ref = 80


""" Plot """
if en_plots:
  plt.figure(figsize = (12, 6))
  plt.subplot(221)
  plt.plot(n, x)  # original signal
  plt.plot(n, y, 'r')  # filtered
  plt.xlabel('sample')
  plt.ylabel('amplitude')
  plt.legend(['x', 'y'])
  plt.title('Input and Output')

  # plt.figure(figsize=(15,9))
  plt.subplot(222)
  plt.title("Adaptation")
  plt.xlabel("samples - k")
  plt.plot(y_r, "b", label="y_ref")
  plt.plot(y, "g", label="y")
  plt.legend()
  plt.subplot(224)
  plt.title("Filter error")
  plt.xlabel("samples")
  plt.plot(10*np.log10(e**2), "r", label="error [dB]")
  plt.legend()

  # Plot the good part of the filtered signal vs a pure 100hz tone
  plt.subplot(223)
  plt.plot(t, y_ref)  # pure 100hz tone
  plt.plot(t[n_taps-1:], y[n_taps-1:], 'r')  # the "good" part of the filtered signal
  plt.xlabel('time')
  plt.ylabel('amplitude')
  plt.legend(['pure tone', 'y (good part)'])
  plt.title('Filter Ouput vs Pure Tone')

  plt.tight_layout()
  plt.show()


""" Write to file """
if en_filegen:
  fpath         = os.path.join(fpath, 'taps{:}_n{:}'.format(n_taps, N))

  fname = os.path.join(fpath, ref_fnm)
  fwrite_array_f32(fname, arr_name=ref_arr_nm, arr=y_ref, arr_size='TOTAL_SAMPLES', per_line=8)

  fname = os.path.join(fpath, output_fnm)
  fwrite_array_f32(fname, arr_name=output_arr_nm, arr=y, arr_size='TOTAL_SAMPLES', per_line=8)

  fname = os.path.join(fpath, input_fnm)
  fwrite_array_f32(fname, arr_name=input_arr_nm, arr=x, arr_size='TOTAL_SAMPLES', per_line=8)

  fname = os.path.join(fpath, header_fnm)
  fwrite_header(fname, n_taps=n_taps,
                t_samples=N_tot, n_samples=N,
                snr_ref=snr_ref, mu=mu,
                input_arr_nm=input_arr_nm, output_arr_nm=output_arr_nm, ref_arr_nm=ref_arr_nm)
