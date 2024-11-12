#include <stdint.h>
#include <stdio.h>

// includes for every benchmark
#include "boardsupport.h"

// includes for this benchmark
#include "test_main.h"
#include "snr.h"

/**
 * @brief Filter state and output
 */

static float32_t output[N_SAMPLES];
static float32_t filter_state [N_TAPS + N_SAMPLES - 1];


/**
 * @brief test_main
 * 
 */
int __attribute__ ((used)) test_main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused)))
{
  uint32_t ccnt;
  uint32_t fail_count = 0;
  float32_t output_initial[N_TAPS];
  uint32_t ptr;

  // filter initialization
  arm_fir_instance_f32 filter_S;
  arm_fir_init_f32(&filter_S, N_TAPS, coeff, filter_state, N_SAMPLES);

  // ignore the first N_TAPS outputs (bad output based on zero initial state)
  for (ptr = 0; ptr < (N_TAPS/N_SAMPLES); ptr++)
  {
    arm_fir_f32(&filter_S, input + (ptr * N_SAMPLES), output_initial + (ptr * N_SAMPLES), N_SAMPLES);
  }

  // begin profiling
  start_trigger();

  arm_fir_f32(&filter_S, (input + N_TAPS), output, N_SAMPLES);

  // end profiling
  stop_trigger();

  // get the cycle count
  ccnt = get_ccnt();

  #ifndef NO_SNR_CHECK
    // calculate SNR of test output vs golden reference
    float32_t snr;
    snr = snr_f32(output_ref, output, N_SAMPLES);

    printf("SNR=%d\n", (int)snr);

    // for (uint16_t i = 0; i < N_SAMPLES; i++)
    // {
    //   printf("output[%d]=%f, expected=%f\n", i, output[i], output_ref[i]);
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
