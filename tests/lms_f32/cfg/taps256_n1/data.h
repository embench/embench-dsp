
#ifndef DATA_H
#define DATA_H

#include "arm_math.h"

#define N_TAPS          (256)
#define TOTAL_SAMPLES   (257)
#define N_SAMPLES       (1)
#define SNR_REF_THLD    (80)

#define N_INITIAL       (TOTAL_SAMPLES-N_SAMPLES)

static float32_t mu =  0.0500000000f;

extern float32_t input[TOTAL_SAMPLES];
extern float32_t ref[TOTAL_SAMPLES];
extern float32_t output_ref[TOTAL_SAMPLES];

#endif  // DATA_H
