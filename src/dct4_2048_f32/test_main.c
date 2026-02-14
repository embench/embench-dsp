#include <stdint.h>
#include <stdio.h>

// includes for every benchmark
#include "boardsupport.h"

// includes for this benchmark
#include "test_main.h"
#include "snr.h"
#include "arm_common_tables.h"


/**
 * @brief Transform state array
 */

static float32_t dct4_state[DCT4_SIZE*2];

float32_t * output = inout;


/**
 * @brief test_main
 * 
 */
int __attribute__ ((used)) test_main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused)))
{
  uint32_t ccnt;
  uint32_t fail_count = 0;

  arm_status status;

  // transform initialization
  // we updated the implementation to use a fast RFFT implementation
  arm_rfft_fast_instance_f32  rfft_S;
  status = arm_rfft_fast_init_2048_f32(&rfft_S);
  if (status != ARM_MATH_SUCCESS)
  {
    printf("TEST FAIL\n");
    return 1;  // fail early
  }
  // static initialization since the library doesn't yet have a non-deprecated init function
  arm_dct4_instance_f32  dct4_S = {DCT4_SIZE, DCT4_SIZE/2, 
                                   0.03125f,          // normalizing factor is sqrt(2/DCT4_SIZE)
                                   Weights_2048,      // twiddle coefficients
                                   cos_factors_2048,  // cosine factors
                                   &rfft_S,           // real FFT instance (pre-initialized)
                                   &(rfft_S.Sint),    // complex FFT instance (initialized by RFFT)
                                   };

  // begin profiling
  start_trigger();

  arm_dct4_f32(&dct4_S, &dct4_state[0], &inout[0]);

  // end profiling
  stop_trigger();

  // get the cycle count
  ccnt = get_ccnt();

  #ifndef NO_SNR_CHECK
    // calculate SNR of test output vs matlab reference output
    float32_t snr;
    snr = snr_f32(output_ref, inout, DCT4_SIZE);

    // check correctness (if reference and actual filter outputs matched)
    fail_count += (snr < SNR_REF_THLD);

    printf("SNR = %i\n", (int)snr);

    // // print output vs reference
    // for (uint16_t i = 0; i < DCT4_SIZE; i++)
    // {
    //   printf("output[%d]=%f, expected=%f, err=%f\n", i, output[i], output_ref[i], output[i]-output_ref[i]);
    // }

    // print to a python list, useful for debug
    // uint32_t ptr;
    // for (ptr = 0; ptr < N_SAMPLES; ptr++)
    // {
    //     if (ptr == 0)
    //         printf("output = [%f, ", *(output + ptr));
    //     else if (ptr == (N_SAMPLES-1))
    //         printf("%f]\n", *(output + ptr));
    //     else
    //         printf("%f,", *(output + ptr));
    // }
  #endif

  if (fail_count)
    printf("TEST FAIL\nCCNT = %i\n", ccnt);
  else
    printf("TEST PASS\nCCNT = %i\n", ccnt);

  return !(fail_count == 0);
}
