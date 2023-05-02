/*
   DataPin.h - Class for fiber inputs on the modules
*/
#ifndef DataPin_h
#define DataPin_h

#include <Arduino.h>
#include <bluefruit.h>
#include "Pin.h"
#include "MiscDefines.h"

class DataPin
{
  public:
    DataPin(Pin *pin_in, Pin *pin_out, BLEUart *bleuart);
    void setup(int read_period, unsigned int data_points_per_batch);
    void set_read_period(int read_period);
    void set_data_points_per_batch(unsigned int data_points_per_batch);
    void set_output_high_on_read(bool output_high_on_read);
    void set_output(int output);
    unsigned short read_data_pin();
    void read_store_data();
    void read_send_one_shot();
    void flush(int num_points);
    void send_data(unsigned short *data_buffer, int num_points);
    void clear_buffer();
    void start(bool empty_buffer);
    void stop();
    void set_send_updates(bool send_updates);
    void send_update(char *message);
    SoftwareTimer read_timer;
    int state;
  private:
    Pin *_pin_in, *_pin_out;
    BLEUart *_bleuart;
    bool _send_updates;
    bool _output_high_on_read;
    unsigned int _data_index; // The position to store the next data point
    unsigned int _data_points_per_batch;
    unsigned short _data_buffer[DATA_POINTS_PER_BUFFER];
};

static void read_timer_callback(TimerHandle_t xTimerID);

#endif
