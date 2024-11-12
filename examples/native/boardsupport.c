/* Copyright (C) 2017 Embecosm Limited and University of Bristol

   Contributor Graham Markall <graham.markall@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <stdint.h>
#include "boardsupport.h"


void
init_board ()
{}

void __attribute__ ((noinline))
start_trigger ()
{}

void __attribute__ ((noinline))
stop_trigger ()
{}

int __attribute__ ((noinline))
get_ccnt ()
{
  return 0;
}
