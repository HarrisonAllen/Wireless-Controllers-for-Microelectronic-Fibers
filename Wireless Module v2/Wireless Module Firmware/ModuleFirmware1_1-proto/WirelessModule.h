/*
   WirelessModule.h - Class for the wireless modules
*/
#ifndef WirelessModule_h
#define WirelessModule_h

#include <Arduino.h>
#include <bluefruit.h>
#include "Pin.h"
#include "LED.h"
#include "DataPin.h"
#include "MiscDefines.h"

class WirelessModule
{
  public:
    WirelessModule(Pin *(*pins)[NUM_PINS], LED *(*leds)[NUM_OUTPUTS], DataPin *(*data_pins)[NUM_INPUTS], BLEUart *bleuart, uint16_t *connection);
    Pin *get_pin(int pin_type, int pin_num);
    LED *get_led(int led_num);
    DataPin *get_data_pin(int data_pin_num);
    BLEUart *get_bleuart();
    uint16_t *get_connection();
    void handle_data(char *data);
    void send_message(char *message);
  private:
    Pin *(*_pins)[NUM_PINS];
    LED *(*_leds)[NUM_OUTPUTS];
    DataPin *(*_data_pins)[NUM_INPUTS];
    BLEUart *_bleuart;
    uint16_t *_connection;
};

static void parse_data(char *data, WirelessModule *wireless_module);

static char *extract_arg(char *str, char *outs, char *delims);

#endif
