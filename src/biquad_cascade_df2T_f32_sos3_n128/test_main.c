#include <stdint.h>
#include <stdio.h>

// includes for every benchmark
#include "boardsupport.h"

// includes for this benchmark
#include "test_main.h"
#include "snr.h"

/**
 * @brief Filter output
 */

static float32_t output[N_SAMPLES];



/**
 * @brief Filter state
 */

static float32_t filter_state [2*N_STAGES];


/**
 * @brief test_main
 * 
 */
int __attribute__ ((used)) test_main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused)))
{
  uint32_t ccnt;
  uint32_t fail_count = 0;
  float32_t output_initial[N_INITIAL];

  // filter initialization
  arm_biquad_cascade_df2T_instance_f32 filter_S;
  arm_biquad_cascade_df2T_init_f32(&filter_S, N_STAGES, coeff, filter_state);

  // ignore the noisy outputs due to initial conditions
  arm_biquad_cascade_df2T_f32(&filter_S, input, output_initial, N_INITIAL);

  // begin profiling
  start_trigger();

  arm_biquad_cascade_df2T_f32(&filter_S, input + N_INITIAL, output, N_SAMPLES);

  // end profiling
  stop_trigger();

  // get the cycle count
  ccnt = get_ccnt();

  #ifndef NO_SNR_CHECK
    // calculate SNR of test output vs matlab reference output
    float32_t snr;
    snr = snr_f32(output_ref, output, N_SAMPLES);

    // check correctness (if reference and actual filter outputs matched)
    fail_count += (snr < SNR_REF_THLD);

    printf("SNR = %i\n", (int)snr);

    // print output vs reference
    // for (uint16_t i = 0; i < N_SAMPLES; i++)
    // {
    //   printf("output[%d]=%f, expected=%f\n", i, output[i], output_ref[i]);
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
