
#ifndef DATA_H
#define DATA_H

#include "arm_math.h"

#define DCT4_SIZE       (2048)
#define SNR_REF_THLD    (100)

extern float32_t inout[DCT4_SIZE];
extern float32_t output_ref[DCT4_SIZE];

#endif  // DATA_H
