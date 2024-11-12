
#ifndef DATA_H
#define DATA_H

#include "arm_math.h"

#define FFT_SIZE        (512)
#define IFFT_FLAG       (0)
#define SNR_REF_THLD    (138)

extern float32_t input[FFT_SIZE];
extern float32_t output_ref[FFT_SIZE];

#endif  // DATA_H
