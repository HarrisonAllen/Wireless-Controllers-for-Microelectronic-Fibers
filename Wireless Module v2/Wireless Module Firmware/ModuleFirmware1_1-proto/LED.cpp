/*
   LED.cpp - Class for fiber LEDS on the modules
 */

#include "LED.h"


LED::LED(Pin *pin_out, BLEUart *bleuart) {
    // Setup pins
    _pin_out = pin_out;

    // Setup other variables
    _bleuart = bleuart;
    state = LS_DISABLED;

    // TODO: Store periods as variables

    // Set some default timer values to avoid crashes
    set_on_period(1000, false);
    set_off_period(4000, false);
    set_led_on_period(10, false);
    set_led_off_period(40, false);
}


void LED::set_periods(int on_period, int off_period, int led_on_period, int led_off_period) {
    stop_loudly();

    // Setup timers
    set_on_period(on_period, false);
    set_off_period(off_period, false);
    set_led_on_period(led_on_period, false);
    set_led_off_period(led_off_period, false);
}

void LED::set_on_period(int on_period, bool should_stop) {
    if (should_stop)
        stop_loudly();
    on_timer.begin(on_period, on_timer_callback, (void *)this, false);
}

void LED::set_off_period(int off_period, bool should_stop) {
    if (should_stop)
        stop_loudly();
    off_timer.begin(off_period, off_timer_callback, (void *)this, false);
}

void LED::set_led_on_period(int led_on_period, bool should_stop) {
    if (should_stop)
        stop_loudly();
    led_on_timer.begin(led_on_period, led_on_timer_callback, (void *)this, false);
}

void LED::set_led_off_period(int led_off_period, bool should_stop) {
    if (should_stop)
        stop_loudly();
    led_off_timer.begin(led_off_period, led_off_timer_callback, (void *)this, false);
}

int LED::get_state() {
    return state;
}

void LED::start() {
    on_timer.start();
    led_on_timer.start();
    state = LS_ON_LED_ON;
}

void LED::stop() {
    on_timer.stop();
    off_timer.stop();
    led_on_timer.stop();
    led_off_timer.stop();
    turn_off_silent();
    state = LS_DISABLED;
}

void LED::stop_loudly() {
    stop();
    send_update("Stopped");
}

void LED::start_loudly() {
    start();
    send_update("Started");
}

void LED::turn_on() {
    _pin_out->set_output(PIN_ON);
    send_update("LED On");
}

void LED::turn_off() {
    _pin_out->set_output(PIN_OFF);
    send_update("LED Off");
}

void LED::turn_on_silent() {
    _pin_out->set_output(PIN_ON);
}

void LED::turn_off_silent() {
    _pin_out->set_output(PIN_OFF);
}

void LED::set_send_updates(bool send_updates) {
    _send_updates = send_updates;
}

void LED::send_update(char *message) {
    if (_send_updates) {
        char update_buffer[40];
        sprintf(update_buffer, "%03dS%c%s", MODULE_ID, ' ' + _pin_out->get_pin_id(), message);
        _bleuart->write(update_buffer, strlen(update_buffer));
    }
}

// On period over, turn off
static void on_timer_callback(TimerHandle_t xTimerID) {
    LED *led = (LED *)pvTimerGetTimerID(xTimerID);
    led->stop();
    led->off_timer.start();
    led->state = LS_OFF;
    led->send_update("Resting");
}

// Off period over, turn on
static void off_timer_callback(TimerHandle_t xTimerID) {
    LED *led = (LED *)pvTimerGetTimerID(xTimerID);
    led->start();
    led->send_update("Pulsing");
}

// LED On period over, turn LED off
static void led_on_timer_callback(TimerHandle_t xTimerID) {
    LED *led = (LED *)pvTimerGetTimerID(xTimerID);
    led->led_off_timer.start();
    led->turn_off_silent();
    led->state = LS_ON_LED_OFF;
}

// LED Off period over, turn LED on
static void led_off_timer_callback(TimerHandle_t xTimerID) {
    LED *led = (LED *)pvTimerGetTimerID(xTimerID);
    led->led_on_timer.start();
    led->turn_on_silent();
    led->state = LS_ON_LED_ON;
}
