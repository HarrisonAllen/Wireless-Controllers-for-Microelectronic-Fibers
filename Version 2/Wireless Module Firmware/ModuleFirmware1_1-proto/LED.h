/*
   LED.h - Class for fiber LEDS on the modules
*/
#ifndef LED_h
#define LED_h

#include <Arduino.h>
#include "Pin.h"

#define LS_DISABLED   0b000
#define LS_OFF        0b001
#define LS_ON_LED_OFF 0b011
#define LS_ON_LED_ON  0b111

#define LS_STOPPED 0
#define LS_PULSING 1
#define LS_RESTING 2

class LED
{
  public:
    LED(Pin *pin_out, BLEUart *bleuart);
    void set_periods(int on_period, int off_period, int led_on_period, int led_off_period);
    void set_on_period(int on_period, bool should_stop);
    void set_off_period(int off_period, bool should_stop);
    void set_led_on_period(int led_on_period, bool should_stop);
    void set_led_off_period(int led_off_period, bool should_stop);
    int get_state();
    void start();
    void stop();
    void stop_loudly();
    void start_loudly();
    void turn_on();
    void turn_off();
    void turn_on_silent();
    void turn_off_silent();
    void set_send_updates(bool send_updates);
    void send_update(char *message);
    SoftwareTimer on_timer;
    SoftwareTimer off_timer;
    SoftwareTimer led_on_timer;
    SoftwareTimer led_off_timer;
    int state;
  private:
    BLEUart *_bleuart;
    Pin *_pin_out;
    bool _send_updates;
};

static void on_timer_callback(TimerHandle_t xTimerID);
static void off_timer_callback(TimerHandle_t xTimerID);
static void led_on_timer_callback(TimerHandle_t xTimerID);
static void led_off_timer_callback(TimerHandle_t xTimerID);

#endif
