/******************************************************************************
 * @file     arm_math_types.h
 * @brief    Public header file for CMSIS DSP Library
 * @version  V1.10.0
 * @date     08 July 2021
 * Target Processor: Cortex-M and Cortex-A cores
 ******************************************************************************/
/*
 * Copyright (c) 2010-2021 Arm Limited or its affiliates. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef ARM_MATH_TYPES_H_

#define ARM_MATH_TYPES_H_

#ifndef ARM_DSP_ATTRIBUTE 
#define ARM_DSP_ATTRIBUTE 
#endif

#ifndef ARM_DSP_TABLE_ATTRIBUTE 
#define ARM_DSP_TABLE_ATTRIBUTE 
#endif

#ifdef   __cplusplus
extern "C"
{
#endif

/* Compiler specific diagnostic adjustment */
#if   defined ( __CC_ARM )

#elif defined ( __ARMCC_VERSION ) && ( __ARMCC_VERSION >= 6010050 )

#elif defined ( __APPLE_CC__ )
  #pragma GCC diagnostic ignored "-Wold-style-cast"

#elif defined(__clang__)
  #pragma GCC diagnostic push
  #pragma GCC diagnostic ignored "-Wsign-conversion"
  #pragma GCC diagnostic ignored "-Wconversion"
  #pragma GCC diagnostic ignored "-Wunused-parameter"

#elif defined ( __GNUC__ )
  #pragma GCC diagnostic push
  #pragma GCC diagnostic ignored "-Wsign-conversion"
  #pragma GCC diagnostic ignored "-Wconversion"
  #pragma GCC diagnostic ignored "-Wunused-parameter"
  // Disable some code having issue with GCC
  #define ARM_DSP_BUILT_WITH_GCC 

#elif defined ( __ICCARM__ )

#elif defined ( __TI_ARM__ )

#elif defined ( __CSMC__ )

#elif defined ( __TASKING__ )

#elif defined ( _MSC_VER )

#else
  #error Unknown compiler
#endif

#include <stdint.h>
#define  __ALIGNED(x) __attribute__((aligned(x)))
#define __STATIC_FORCEINLINE static
#define __STATIC_INLINE static
#define __WEAK



#include <string.h>
#include <math.h>
#include <float.h>
#include <limits.h>

/**
 * @defgroup genericTypes Generic Types
 * @{
*/

 /**
   * @brief 8-bit fractional data type in 1.7 format.
   */
  typedef int8_t q7_t;

  /**
   * @brief 16-bit fractional data type in 1.15 format.
   */
  typedef int16_t q15_t;

  /**
   * @brief 32-bit fractional data type in 1.31 format.
   */
  typedef int32_t q31_t;

  /**
   * @brief 64-bit fractional data type in 1.63 format.
   */
  typedef int64_t q63_t;

  /**
   * @brief 32-bit floating-point type definition.
   */
  typedef float float32_t;

  /**
   * @brief 64-bit floating-point type definition.
   */
  typedef double float64_t;

  /**
   * @brief Error status returned by some functions in the library.
   */
  typedef enum
  {
    ARM_MATH_SUCCESS                 =  0,        /**< No error */
    ARM_MATH_ARGUMENT_ERROR          = -1,        /**< One or more arguments are incorrect */
    ARM_MATH_LENGTH_ERROR            = -2,        /**< Length of data buffer is incorrect */
    ARM_MATH_SIZE_MISMATCH           = -3,        /**< Size of matrices is not compatible with the operation */
    ARM_MATH_NANINF                  = -4,        /**< Not-a-number (NaN) or infinity is generated */
    ARM_MATH_SINGULAR                = -5,        /**< Input matrix is singular and cannot be inverted */
    ARM_MATH_TEST_FAILURE            = -6,        /**< Test Failed */
    ARM_MATH_DECOMPOSITION_FAILURE   = -7         /**< Decomposition Failed */
  } arm_status;

/**
 * @} // endgroup generic
*/


#define F64_MAX   ((float64_t)DBL_MAX)
#define F32_MAX   ((float32_t)FLT_MAX)



#define F64_MIN   (-DBL_MAX)
#define F32_MIN   (-FLT_MAX)



#define F64_ABSMAX   ((float64_t)DBL_MAX)
#define F32_ABSMAX   ((float32_t)FLT_MAX)



#define F64_ABSMIN   ((float64_t)0.0)
#define F32_ABSMIN   ((float32_t)0.0)


#define Q31_MAX   ((q31_t)(0x7FFFFFFFL))
#define Q15_MAX   ((q15_t)(0x7FFF))
#define Q7_MAX    ((q7_t)(0x7F))
#define Q31_MIN   ((q31_t)(0x80000000L))
#define Q15_MIN   ((q15_t)(0x8000))
#define Q7_MIN    ((q7_t)(0x80))

#define Q31_ABSMAX   ((q31_t)(0x7FFFFFFFL))
#define Q15_ABSMAX   ((q15_t)(0x7FFF))
#define Q7_ABSMAX    ((q7_t)(0x7F))
#define Q31_ABSMIN   ((q31_t)0)
#define Q15_ABSMIN   ((q15_t)0)
#define Q7_ABSMIN    ((q7_t)0)

  /* Dimension C vector space */
  #define CMPLX_DIM 2

#ifdef   __cplusplus
}
#endif

#endif /*ifndef _ARM_MATH_TYPES_H_ */
