/*
   Pin.cpp - Class for pins on the modules
 */

#include "Pin.h"

Pin::Pin(int pin, int id, BLEUart *bleuart) {
    _pin = pin;
    _id = id;
    _bleuart = bleuart;
    set_mode(PM_INPUT);
}

void Pin::set_pin(int pin) {
    _pin = pin;
}

void Pin::set_mode(int mode) {
    _mode = mode;
    switch (mode) {
        case PM_INPUT:
            pinMode(_pin, INPUT);
            send_update("Input");
            break;
        case PM_INPUT_PULLUP:
            pinMode(_pin, INPUT_PULLUP);
            send_update("Input Pullup");
            break;
        case PM_OUTPUT_LOW:
            pinMode(_pin, OUTPUT);
            digitalWrite(_pin, LOW);
            send_update("Output Low");
            break;
        case PM_OUTPUT_HIGH:
            pinMode(_pin, OUTPUT);
            digitalWrite(_pin, HIGH);
            send_update("Output High");
            break;
        case PM_HIGH_DRIVE_LOW:
            nrf_gpio_cfg(_pin, 
                         NRF_GPIO_PIN_DIR_OUTPUT, 
                         NRF_GPIO_PIN_INPUT_DISCONNECT, 
                         NRF_GPIO_PIN_NOPULL, 
                         NRF_GPIO_PIN_S0H1, 
                         NRF_GPIO_PIN_NOSENSE);
            digitalWrite(_pin, LOW);
            break;
        case PM_HIGH_DRIVE_HIGH:
            nrf_gpio_cfg(_pin, 
                         NRF_GPIO_PIN_DIR_OUTPUT, 
                         NRF_GPIO_PIN_INPUT_DISCONNECT, 
                         NRF_GPIO_PIN_NOPULL, 
                         NRF_GPIO_PIN_S0H1, 
                         NRF_GPIO_PIN_NOSENSE);
            digitalWrite(_pin, HIGH);
            break;
        default:
            pinMode(_pin, INPUT);
            send_update("Input");
            break;
    }
}

unsigned short Pin::read_pin() {
    if (is_input()) {
        return analogRead(_pin);
    }
    return 0;
}

// Output is either HIGH/PIN_ON or LOW/PIN_OFF
bool Pin::set_output(int output) {
    if (is_output()) {
        if (output == PIN_ON) {
            set_mode(PM_OUTPUT_HIGH);
        } else if (output == PIN_OFF) {
            set_mode(PM_OUTPUT_LOW);
        }
        return true;
    }
    return false;
}

bool Pin::toggle_output() {
    if (is_output()) {
        if (_mode == PM_OUTPUT_HIGH) {
            set_output(PIN_OFF);
        } else if (_mode == PM_OUTPUT_LOW) {
            set_output(PIN_ON);
        }
        return true;
    }
    return false;
}

bool Pin::is_input() {
    return _is_mode_input(_mode);
}

bool Pin::is_output() {
    return _is_mode_output(_mode);
}

int Pin::get_pin_state() {
    return _mode;
}

byte Pin::get_pin_id() {
    return _id;
}

void Pin::set_send_updates(bool send_updates) {
    _send_updates = send_updates;
}

void Pin::send_update(char *message) {
    if (_send_updates) {
        char update_buffer[40];
        sprintf(update_buffer, "%03dS%c%s", MODULE_ID, ' ' + _id, message);
        _bleuart->write(update_buffer, strlen(update_buffer));
    }
}

bool Pin::_is_mode_input(int mode) {
    return (mode == PM_INPUT || mode == PM_INPUT_PULLUP);
}

bool Pin::_is_mode_output(int mode) {
    return (mode == PM_OUTPUT_LOW || mode == PM_OUTPUT_HIGH);
}