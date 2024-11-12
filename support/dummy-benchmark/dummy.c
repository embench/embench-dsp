/* Common dummy benchmark

   Copyright (C) 2018-2024 Embecosm Limited

   Contributor: Konrad Moron <konrad.moron@tum.de>

   SPDX-License-Identifier: GPL-3.0-or-later */

/* This is just a wrapper for the board specific support file. */
int __attribute__ ((used, noinline)) test_main (int argc __attribute__ ((unused)), char *argv[] __attribute__ ((unused))) {
  return 0;
}

#undef MAGIC