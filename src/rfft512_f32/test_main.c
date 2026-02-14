#include <stdint.h>
#include <stdio.h>

// includes for every benchmark
#include "boardsupport.h"

// includes for this benchmark
#include "test_main.h"
#include "snr.h"

/**
 * @brief Input and Reference Output
 *      - See data/
 */

// Test Result
static float32_t output[FFT_SIZE];


/**
 * @brief test_main
 * 
 */
int __attribute__ ((used)) test_main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused)))
{
  uint32_t ccnt;
  uint32_t fail_count = 0;

  arm_status status;

  // initialization
  arm_rfft_fast_instance_f32 arm_rfft_fast_S;
  status = arm_rfft_fast_init_512_f32(&arm_rfft_fast_S);
  if (status != ARM_MATH_SUCCESS)
  {
    printf("TEST FAIL\n");
    return 1;  // fail early
  }

  // begin profiling
  start_trigger();

  arm_rfft_fast_f32(&arm_rfft_fast_S, input, output, IFFT_FLAG);

  // end profiling
  stop_trigger();

  // get the cycle count
  ccnt = get_ccnt();

  #ifndef NO_SNR_CHECK
    // calculate SNR of test output vs golden reference
    float32_t snr;
    snr = snr_f32(output_ref, output, FFT_SIZE);

    printf("SNR = %i\n", (int)snr);

    // check correctness (if reference and actual filter outputs matched)
    fail_count += (snr < SNR_REF_THLD);
  #endif

  if (fail_count)
    printf("TEST FAIL\n");
  else
    printf("TEST PASS\nCCNT = %i\n", ccnt);

  return !(fail_count == 0);
}
