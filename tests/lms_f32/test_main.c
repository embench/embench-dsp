#include <stdint.h>
#include <stdio.h>

// includes for every benchmark
#include "boardsupport.h"

// includes for this benchmark
#include "data.h"
#include "snr.h"

/**
 * @brief Filter state and output
 */

static float32_t out[TOTAL_SAMPLES];
static float32_t err[TOTAL_SAMPLES];
static float32_t filter_state[N_TAPS + N_SAMPLES - 1];


/**
 * @brief test_main
 * 
 */
int __attribute__ ((used)) test_main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused)))
{
  uint32_t ccnt;
  uint32_t fail_count = 0;
  uint32_t ptr;

  // filter initialization
  arm_lms_instance_f32 filter_S;
  float32_t coeff[N_TAPS] = {0};

  arm_lms_init_f32(&filter_S, N_TAPS, coeff, filter_state, mu, N_SAMPLES);

  // ignore the first N_INITIAL outputs (bad output based on zero initial state)
  for (ptr = 0; ptr < (N_INITIAL/N_SAMPLES); ptr++)
  {
    arm_lms_f32(&filter_S, input + (ptr * N_SAMPLES), ref + (ptr * N_SAMPLES), out + (ptr * N_SAMPLES), err + (ptr * N_SAMPLES), N_SAMPLES);
  }

  // begin profiling
  start_trigger();

  arm_lms_f32(&filter_S, input + N_INITIAL, ref + N_INITIAL, out + N_INITIAL, err + N_INITIAL, N_SAMPLES);

  // end profiling
  stop_trigger();

  // get the cycle count
  ccnt = get_ccnt();

  #ifndef NO_SNR_CHECK
    // calculate SNR of test output vs golden reference
    float32_t snr;
    snr = snr_f32(output_ref + N_INITIAL, out + N_INITIAL, N_SAMPLES);

    printf("SNR=%d\n", (int)snr);

    // for (uint16_t i = 0; i < TOTAL_SAMPLES; i++)
    // {
    //   printf("out[%d]=%f, expected=%f\n", i, out[i], output_ref[i]);
    // }

    // check correctness (if reference and actual filter outputs matched)
    fail_count += (snr < SNR_REF_THLD);
  #endif

  if (fail_count)
    printf("TEST FAIL\n");
  else
    printf("TEST PASS\nCCNT = %i\n", ccnt);

  return !(fail_count == 0);
}
