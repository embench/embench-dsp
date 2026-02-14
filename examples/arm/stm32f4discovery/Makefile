##############################################################
# INIT
##############################################################

TGT_SRC    :=
TGT_INC    :=
TGT_DEF    :=
TGT_OBJ    :=

# may be initialized/modified elsewhere with global settings
TGT_FLG    +=


##############################################################
# EXTERNAL
##############################################################


##############################################################
# TARGET
##############################################################

### ISA
TGT_ISA     =-mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb 

### DEFINES
TGT_DEF    +=-DSTM32F407xx

### INCLUDES
TGT_INC    +=-I $(TGT_DIR)/.. -I $(TGT_DIR)

### FLAGS
TGT_FLG    +=$(TGT_ISA) $(TGT_DEF) -Os

libstartup.a: startup.o system_stm32f4.o syscalls.o
	arm-none-eabi-ar rcs $@ $^

startup.o: startup.S
	arm-none-eabi-gcc -c -o $@ $^ $(TGT_FLG)

syscalls.o: syscalls.c
	arm-none-eabi-gcc -c -o $@ $^ $(TGT_FLG)

system_stm32f4.o: system_stm32f4.c
	arm-none-eabi-gcc -c -o $@ $^ $(TGT_FLG)

clean:
	rm -rf libstartup.a *.o

.PHONY: clean