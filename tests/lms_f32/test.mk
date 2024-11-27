##############################################################
# INIT
##############################################################

TST_SRC    :=
TST_INC    :=
TST_DEF    :=
TST_OBJ    :=

# may be initialized/modified elsewhere with global settings
TST_FLG    +=


##############################################################
# EXTERNAL
##############################################################

### global options for all library users
include $(ROOT)/dsp_inc.mk
TST_INC    +=$(DSP_INC)
TST_DEF    +=$(DSP_DEF)

### snr checker
TST_INC    +=-I $(CMN_DIR)
TST_SRC    +=$(CMN_DIR)/snr.c


##############################################################
# TEST
##############################################################

ifeq ($(CFG),)
  CFG       =taps256_n128
  $(warning WARNING: CFG not set for $(TEST). Defaulting to CFG=taps256_n128)
endif

### DEFINES
TST_DEF    +=

### INCLUDES
TST_INC    +=-I $(TST_DIR)
TST_INC    +=-I $(TST_DIR)/configs/$(CFG)

### FLAGS
TST_FLG    +=$(TST_DEF)

### SOURCES
TST_SRC    +=$(TST_DIR)/test_main.c
TST_SRC    +=$(DSP_DIR)/source/FilteringFunctions/arm_lms_f32.c
TST_SRC    +=$(DSP_DIR)/source/FilteringFunctions/arm_lms_init_f32.c

# data files
TST_SRC    +=$(TST_DIR)/configs/$(CFG)/in.c
TST_SRC    +=$(TST_DIR)/configs/$(CFG)/ref.c
TST_SRC    +=$(TST_DIR)/configs/$(CFG)/out.c

### OBJECTS
TST_OBJ    +=$(patsubst %.c,%.o, $(patsubst %.S,%.o,$(notdir $(TST_SRC))))
