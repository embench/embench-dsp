# Embench&#x2122; DSP Golden Reference User Guide

## Requirements
Python 3 with matplotlib, numpy, scipy, and padasip packages.

Validated: Python 3.9.6
```sh
cd ./golden-ref
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running a script
Example:
```sh
./golden-ref/rfft2048_f32/rfft_2048.py
```

## Test cases
For the provided tests, below outlines the high-level test cases generated per script:

biquad_cascade_df2T_f32:
- Sampling frequency: 48 kHz
- Order: 6 (i.e. 3 second-order stages)
- Filter type: Butterworth Low-Pass Filter, Cutoff frequency = 1 kHz
- Input content: 0.1, 4, and 8 kHz tones at -30, -20, and -10 dB amplitude respectively
- Output SNR is captured for N samples after the noise from initial conditions becomes marginal

dct4_512_f32 and dct4_2048_f32:
- Sampling frequency: 48 kHz
- Input content: 0.1, 4, and 8 kHz tones at -30, -20, and -10 dB amplitude respectively; Zero-mean Gaussian white noise added at -25 dB amplitude

fir_f32:
- Sampling frequency: 48 kHz
- Taps: 256
- Input content: 0.1, 4, and 8 kHz tones at -10, -20, and -10 dB amplitude respectively; Zero-mean Gaussian white noise added at -30 dB amplitude

lms_f32:
- Sampling frequency: 48 kHz
- Taps: 256
- mu: 0.05
- Reference (training) content: 0.1 kHz tone at -10 dB amplitude
- Input content: 0.1, 4, and 8 kHz tones at -10, -20, and -10 dB amplitude respectively

rfft_512_f32:
- Sampling frequency: 48 kHz
- Input content: 0.1, 4, and 8 kHz tones at -25, -20, and -10 dB amplitude respectively; Zero-mean Gaussian white noise added at -20 dB amplitude

rfft_2048_f32:
- Sampling frequency: 48 kHz
- Input content: 0.1, 4, and 8 kHz tones at -30, -20, and -10 dB amplitude respectively; Zero-mean Gaussian white noise added at -20 dB amplitude

## Modifying the test
By default, each script generates C files in a "generated" folder under the script directory.  These may be copied to a benchmark directory in [`src`](./src) to overwrite the test case.

Each script has top-level settings to enable/disable plots and/or file generation. If the script supports generating test cases for a variable number of samples, this is provided as a top-level parameter "N".