/* Copyright (C) 2017 Embecosm Limited and University of Bristol

   Contributor Graham Markall <graham.markall@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#ifndef _SUPPORT_H_
#define _SUPPORT_H_

void init_board(void);
void start_trigger(void);
void stop_trigger(void);
int get_ccnt(void);

#endif

