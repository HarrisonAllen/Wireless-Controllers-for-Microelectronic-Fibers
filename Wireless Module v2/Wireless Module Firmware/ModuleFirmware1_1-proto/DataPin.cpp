/*
   DataPin.h - Class for fiber inputs on the modules
*/

#include "DataPin.h"

DataPin::DataPin(Pin *pin_in, Pin *pin_out, BLEUart *bleuart) {
    _pin_in = pin_in;
    _pin_out = pin_out;
    _bleuart = bleuart;

    // TODO: Store read_period as a variable

    // Initialize read timer as one shot to avoid crashes
    read_timer.begin(500, read_timer_callback, (void *)this, false);
}

void DataPin::setup(int read_period, unsigned int data_points_per_batch) {
    set_read_period(read_period);
    set_data_points_per_batch(data_points_per_batch);
}

void DataPin::set_read_period(int read_period) {
    stop();
    read_timer.begin(read_period, read_timer_callback, (void *)this, true);
    clear_buffer();
}

void DataPin::set_data_points_per_batch(unsigned int data_points_per_batch) {
    if (data_points_per_batch == 0) {
        _data_points_per_batch = DATA_POINTS_PER_BUFFER;
    } else {
        _data_points_per_batch = min(data_points_per_batch, DATA_POINTS_PER_BUFFER);
    }
}

void DataPin::set_output_high_on_read(bool output_high_on_read) {
    _output_high_on_read = output_high_on_read;
}

void DataPin::set_output(int output) {
    _pin_out->set_output(output);
}

unsigned short DataPin::read_data_pin() {
    unsigned short calibration_data = _pin_in->read_pin();
    if (_output_high_on_read) {
        _pin_out->set_output(PIN_ON);
    }
    unsigned short pin_data = _pin_in->read_pin();
    if (_output_high_on_read) {
        _pin_out->set_output(PIN_OFF);
    }
    return pin_data - (_output_high_on_read ? calibration_data : 0);
}

void DataPin::read_store_data() {
    unsigned short data_point = read_data_pin();
    _data_buffer[_data_index] = data_point;
    _data_index++;
    if (_data_index >= _data_points_per_batch) { // TODO: Check if this overflows
        flush(_data_points_per_batch);
    }
}

void DataPin::read_send_one_shot() {
    unsigned short data_point = read_data_pin();
    unsigned short temp_data_buffer[1];
    temp_data_buffer[0] = data_point;
    send_data(temp_data_buffer, 1);
}

void DataPin::flush(int num_points) {
    if (num_points <= 0) {
        num_points = sizeof(_data_buffer);
    } else {
        num_points = min(num_points, sizeof(_data_buffer));
    }
    send_data(_data_buffer, num_points);
    clear_buffer();
}

void DataPin::send_data(unsigned short *data_buffer, int num_points) {
    while (num_points > 0) {
        int points_to_send = min(num_points, MAX_POINTS_PER_SEND);
        // TODO: send read_period, maybe do %05X, max 1048575
        // TODO: Add ~ to end of prefix
        char send_buffer[points_to_send * 2 + 10];
        sprintf(send_buffer, "%03d%c%c", MODULE_ID, points_to_send == 1 ? 'd' : 'D', ' ' + _pin_in->get_pin_id());
        if (points_to_send == 1) {
           sprintf(&send_buffer[5], "%05d", data_buffer[0]);
        } else {
            memcpy(&send_buffer[5], data_buffer, points_to_send * 2);
        }
        _bleuart->write(send_buffer, points_to_send * 2 + 10);

        num_points -= points_to_send;
        data_buffer = &data_buffer[points_to_send];
        // char debug_buffer[40];
        // sprintf(debug_buffer, "Still have %d to send", num_points);
        // _send_updates = true;
        // send_update(debug_buffer);
    }
    
    // if (num_points > 0) {
    //     // send_data(&data_buffer[points_to_send], num_points);
    //     send_data(NULL, num_points);
    // }
    
    // char send_buffer[num_points * 2 + 10];
    // sprintf(send_buffer, "%03d%c%c", MODULE_ID, num_points == 1 ? 'd' : 'D', ' ' + _pin_in->get_pin_id());
    // if (num_points == 1) {
    //    sprintf(&send_buffer[5], "%05d", data_buffer[0]);
    // } else {
    //     memcpy(&send_buffer[5], data_buffer, num_points * 2);
    // }
    // _bleuart->write(send_buffer, num_points * 2 + 10);
    
    // byte send_buffer[num_points * 2 + 3];
    // send_buffer[0] = (byte)MODULE_ID;
    // send_buffer[1] = num_points == 1 ? 'd' : 'D';
    // send_buffer[2] = _pin_in->get_pin_id();
    // memcpy(&send_buffer[3], data_buffer, num_points * 2);
    // _bleuart->write(send_buffer, num_points * 2 + 3);
}

void DataPin::clear_buffer() {
    memset(_data_buffer, 0, sizeof(_data_buffer));
    _data_index = 0;
}

void DataPin::start(bool empty_buffer) {
    if (empty_buffer) {
        clear_buffer();
    }
    read_timer.start();
    send_update("Starting");
}

void DataPin::stop() {
    read_timer.stop();
    send_update("Stopped");
}

void DataPin::set_send_updates(bool send_updates) {
    _send_updates = send_updates;
}

void DataPin::send_update(char *message) {
    if (_send_updates) {
        char update_buffer[40];
        sprintf(update_buffer, "%03dS%c%s", MODULE_ID, ' ' + _pin_out->get_pin_id(), message);
        _bleuart->write(update_buffer, strlen(update_buffer));
    }
}

static void read_timer_callback(TimerHandle_t xTimerID) {
    DataPin *data_pin = (DataPin *)pvTimerGetTimerID(xTimerID);
    data_pin->read_store_data();
}