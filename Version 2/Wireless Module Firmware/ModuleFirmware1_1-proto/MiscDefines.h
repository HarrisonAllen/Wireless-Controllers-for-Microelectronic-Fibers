/*
   MiscDefines.h - Some miscellaneous defines to share across files
*/
#ifndef MiscDefines_h
#define MiscDefines_h

// Change for each individual module
#define MODULE_ID 17

#define NUM_PINS 8
#define NUM_OUTPUTS 4
#define NUM_INPUTS 4
#define NUM_PAIRS 4
#define DATA_POINTS_PER_BUFFER 1000
#define MAX_POINTS_PER_SEND 100 // May need to change based on what else gets sent
#define INPUT_PINS 0
#define OUTPUT_PINS 1
#define INPUT_PIN_ID 0
#define OUTPUT_PIN_ID 1

#define MODULE_ID_OVERRIDE 999

// Change for each module version
#define MODULE_VERSION "1.1P"
#define INPUT_PIN_0 3
#define INPUT_PIN_1 2
#define INPUT_PIN_2 28
#define INPUT_PIN_3 29
#define OUTPUT_PIN_0 21
#define OUTPUT_PIN_1 16
#define OUTPUT_PIN_2 14
#define OUTPUT_PIN_3 12
const int INPUT_PIN_NUMS[] = {INPUT_PIN_0, INPUT_PIN_1, INPUT_PIN_2, INPUT_PIN_3};
const int OUTPUT_PIN_NUMS[] = {OUTPUT_PIN_0, OUTPUT_PIN_1, OUTPUT_PIN_2, OUTPUT_PIN_3};

#endif
