/*
   Pin.h - Class for pins on the modules
*/
#ifndef Pin_h
#define Pin_h

#include <Arduino.h>
#include <bluefruit.h>
#include "MiscDefines.h"

#define PM_INPUT           0b000
#define PM_INPUT_PULLUP    0b001
#define PM_OUTPUT_LOW      0b010
#define PM_OUTPUT_HIGH     0b011
#define PM_HIGH_DRIVE_LOW  0b100
#define PM_HIGH_DRIVE_HIGH 0b101

#define PIN_ON HIGH
#define PIN_OFF LOW

class Pin
{
  public:
    Pin(int pin, int id, BLEUart *bleuart);
    void set_pin(int pin);
    void set_mode(int mode);
    unsigned short read_pin();
    bool set_output(int output);
    bool toggle_output();
    bool is_input();
    bool is_output();
    int get_pin_state();
    byte get_pin_id();
    void set_send_updates(bool send_updates);
    void send_update(char *message);
  private:
    int _pin;
    int _mode;
    BLEUart *_bleuart;
    bool _send_updates;
    byte _id;
    bool _is_mode_input(int mode);
    bool _is_mode_output(int mode);
};

#endif
