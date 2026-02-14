#include <stdint.h>
#include <stdio.h>

#include "support.h"

extern int test_main();


/**
 * @brief main
 * 
 */
int __attribute__ ((used)) main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused)))
{
    uint32_t res;

    init_board();
    
    res = test_main();

    return res;
}
