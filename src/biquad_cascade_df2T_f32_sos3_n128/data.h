
#ifndef DATA_H
#define DATA_H

#include "arm_math.h"

#define N_STAGES        (3)
#define TOTAL_SAMPLES   (235)
#define N_SAMPLES       (128)
#define N_INITIAL       (107)
#define SNR_REF_THLD    (100)

extern float32_t coeff[N_STAGES*5];
extern float32_t input[TOTAL_SAMPLES];
extern float32_t output_ref[N_SAMPLES];

#endif  // DATA_H
