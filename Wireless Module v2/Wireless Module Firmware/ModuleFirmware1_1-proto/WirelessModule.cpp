/*
   
   WirelessModule.cpp - Class for the wireless modules
 */

#include "WirelessModule.h"


WirelessModule::WirelessModule(Pin *(*pins)[NUM_PINS], LED *(*leds)[NUM_OUTPUTS], DataPin *(*data_pins)[NUM_INPUTS], BLEUart *bleuart, uint16_t *connection) {
    _pins = pins;
    _leds = leds;
    _data_pins = data_pins;
    _bleuart = bleuart;
    _connection = connection;
}

Pin *WirelessModule::get_pin(int pin_type, int pin_num) {
    if (pin_type != INPUT_PINS && pin_type != OUTPUT_PINS) {
        return NULL;
    }
    if (pin_num < 0 || pin_num >= NUM_PAIRS) {
        return NULL;
    }
    return (*_pins)[pin_type * NUM_PAIRS + pin_num];
}

LED *WirelessModule::get_led(int led_num) {
    if (led_num < 0 || led_num >= NUM_OUTPUTS) {
        return NULL;
    }
    return (*_leds)[led_num];
}

DataPin *WirelessModule::get_data_pin(int data_pin_num) {
    if (data_pin_num < 0 || data_pin_num >= NUM_INPUTS) {
        return NULL;
    }
    return (*_data_pins)[data_pin_num];
}

BLEUart *WirelessModule::get_bleuart() {
    return _bleuart;
}

uint16_t *WirelessModule::get_connection() {
  return _connection;
}

void WirelessModule::handle_data(char *data) {
    parse_data(data, this);
}

static void parse_data(char *data, WirelessModule *wireless_module) {
  char cmd_delim[2] = ";";
  char arg_delims[2] = ",";
  char *cmd_token;
  cmd_token = strtok(data, cmd_delim);

  // Check that this set of commands is for this module
  char module_id_buff[10] = {0};
  sprintf(module_id_buff, "%s", cmd_token);
  int module_id = atoi(module_id_buff);
  if (module_id != MODULE_ID && module_id != MODULE_ID_OVERRIDE) {
    return;
  }

  cmd_token = strtok(NULL, cmd_delim);
  while (cmd_token != NULL) {
    char cmd_buff[100] = {0};
    sprintf(cmd_buff, "%s", cmd_token);
    char *arg_pos = cmd_buff;
    char arg_buff[40] = {0};

    arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);    
    // Parse command
    if (strcmp(arg_buff, "S") == 0) { // Set pin state
      // 1. Pin number (int)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      int pin_num = atoi(arg_buff);

      // 2. Pin IO/option (single char)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
      char pin_io = arg_buff[0];

      // 3. Pin mode (single char)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
      char pin_mode = arg_buff[0];
      
      if (pin_io == 'P') { // set pins based on presets
        switch (pin_mode) {
          case 'G': // Ground
            wireless_module->get_pin(INPUT_PINS, pin_num)->set_mode(PM_OUTPUT_LOW);
            break;
          case 'L': // LED
            wireless_module->get_pin(INPUT_PINS, pin_num)->set_mode(PM_INPUT);
            wireless_module->get_pin(OUTPUT_PINS, pin_num)->set_mode(PM_OUTPUT_LOW);
            // wireless_module->get_pin(OUTPUT_PINS, pin_num)->set_mode(PM_HIGH_DRIVE_LOW);
            break;
          case 'N': // NTC
            wireless_module->get_pin(INPUT_PINS, pin_num)->set_mode(PM_INPUT);
            wireless_module->get_pin(OUTPUT_PINS, pin_num)->set_mode(PM_OUTPUT_LOW);
            wireless_module->get_data_pin(pin_num)->set_output_high_on_read(true);
            break;
          case 'D': // Data
            wireless_module->get_pin(INPUT_PINS, pin_num)->set_mode(PM_INPUT);
            wireless_module->get_pin(OUTPUT_PINS, pin_num)->set_mode(PM_OUTPUT_LOW);
            break;
          default:
            break;
        }
      } else { // Set each pin individually
        int pin_io_index = pin_io == 'I' ? INPUT_PINS : OUTPUT_PINS;
        switch (pin_mode) {
          case 'l':
            wireless_module->get_pin(pin_io_index, pin_num)->set_mode(PM_OUTPUT_LOW);
            break;
          case 'h':
            wireless_module->get_pin(pin_io_index, pin_num)->set_mode(PM_OUTPUT_HIGH);
            break;
          case 'L':
            wireless_module->get_pin(pin_io_index, pin_num)->set_mode(PM_HIGH_DRIVE_LOW);
            break;
          case 'H':
            wireless_module->get_pin(pin_io_index, pin_num)->set_mode(PM_HIGH_DRIVE_HIGH);
            break;
          case 'I':
            wireless_module->get_pin(pin_io_index, pin_num)->set_mode(PM_INPUT);
            break;
          case 'P':
            wireless_module->get_pin(pin_io_index, pin_num)->set_mode(PM_INPUT_PULLUP);
            break;
          default:
            break;
        }
      }
    } else if (strcmp(arg_buff, "P") == 0) { // Control Pins
      // 1. Pin number (int)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      int pin_num = atoi(arg_buff);
      
      // 2. Pin IO (char)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      char pin_io = arg_buff[0];
      int pin_io_index = pin_io == 'I' ? INPUT_PINS : OUTPUT_PINS;

      // 3. Pin command (int)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
      char pin_cmd = arg_buff[0];

      if (pin_cmd == 'R') { // Read pin
        char read_buff[20];
        int pin_data = wireless_module->get_pin(pin_io_index, pin_num)->read_pin();
        sprintf(read_buff, "%03dd%c%05d", MODULE_ID, ' ' + wireless_module->get_pin(pin_io_index, pin_num)->get_pin_id(), pin_data);
        wireless_module->get_bleuart()->write(read_buff, strlen(read_buff));
      } else if (pin_cmd == 'L' || pin_cmd == 'l' || pin_cmd == '0') { // Set pin low
        wireless_module->get_pin(pin_io_index, pin_num)->set_output(LOW);
      } else if (pin_cmd == 'H' || pin_cmd == 'h' || pin_cmd == '1') { // Set pin high
        wireless_module->get_pin(pin_io_index, pin_num)->set_output(HIGH);
      } else if (pin_cmd == 'U') {
        wireless_module->get_pin(pin_io_index, pin_num)->set_send_updates(true);
      } else if (pin_cmd == 'u') {
        wireless_module->get_pin(pin_io_index, pin_num)->set_send_updates(false);
      }
    } else if (strcmp(arg_buff, "L") == 0) { // Control LEDs
      // 1. LED number (int)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      int led_num = atoi(arg_buff);
      
      // 2. LED command (char)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      char led_cmd = arg_buff[0];
      int on_period, off_period, led_on_period, led_off_period;

      switch (led_cmd) {
        case 'C': // Constructor
          // 1. On Period (int)
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          on_period = atoi(arg_buff);

          // 2. Off Period (int)
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          off_period = atoi(arg_buff);

          // 3. LED On Period (int)
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          led_on_period = atoi(arg_buff);

          // 4. LED Off Period (int)
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          led_off_period = atoi(arg_buff);
          wireless_module->get_led(led_num)->set_periods(on_period, off_period, led_on_period, led_off_period);
          break;
        case 'N': // Set On Period
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          on_period = atoi(arg_buff);
          wireless_module->get_led(led_num)->set_on_period(on_period, true);
          break;
        case 'F': // Set Off Period
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          off_period = atoi(arg_buff);
          wireless_module->get_led(led_num)->set_off_period(off_period, true);
          break;
        case 'n': // Set LED On Period
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          led_on_period = atoi(arg_buff);
          wireless_module->get_led(led_num)->set_led_on_period(led_on_period, true);
          break;
        case 'f': // Set LED Off Period
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
          led_off_period = atoi(arg_buff);
          wireless_module->get_led(led_num)->set_led_off_period(led_off_period, true);
          break;
        case 'S': // Start
          wireless_module->get_led(led_num)->start_loudly();
          break;
        case 's': // Stop
          wireless_module->get_led(led_num)->stop_loudly();
          break;
        case 'R': // Restart
          wireless_module->get_led(led_num)->stop_loudly();
          wireless_module->get_led(led_num)->start_loudly();
          break;
        case 'O': // Turn On
          wireless_module->get_led(led_num)->turn_on();
          break;
        case 'o': // Turn Off
          wireless_module->get_led(led_num)->turn_off();
          break;
        case 'U': // Send Updates Enabled
          wireless_module->get_led(led_num)->set_send_updates(true);
          break;
        case 'u': // Send Updates Disabled
          wireless_module->get_led(led_num)->set_send_updates(false);
          break;
        default:
          break;
      }
    } else if (strcmp(arg_buff, "D") == 0) { // Control Data Pins
      // 1. Data Pin # (int)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      int data_pin_num = atoi(arg_buff);
      
      // 2. Data Pin command (char)
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);  
      char data_pin_cmd = arg_buff[0];

      int read_period, data_points_per_batch, num_points_to_flush;

      switch (data_pin_cmd) {
        case 'C': // Constructor
          // 1. Read Period (int)
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
          read_period = atoi(arg_buff);

          // 2. Data Points Per Batch (int)
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
          data_points_per_batch = atoi(arg_buff);
          
          wireless_module->get_data_pin(data_pin_num)->setup(read_period, data_points_per_batch);
          break;
        case 'P': // Set Read Period
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
          read_period = atoi(arg_buff);
          wireless_module->get_data_pin(data_pin_num)->set_read_period(read_period);
          break;
        case 'd': // Set Data Points Per Batch
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
          data_points_per_batch = atoi(arg_buff);
          wireless_module->get_data_pin(data_pin_num)->set_data_points_per_batch(data_points_per_batch);
          break;
        case 'r': // Read and Store Data
          wireless_module->get_data_pin(data_pin_num)->read_store_data();
          break;
        case 'R': // Read and Send One Shot
          wireless_module->get_data_pin(data_pin_num)->read_send_one_shot();
          break;
        case 'F': // Flush
          arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
          num_points_to_flush = atoi(arg_buff);
          wireless_module->get_data_pin(data_pin_num)->flush(num_points_to_flush);
          break;
        case 'c': // Clear buffer
          wireless_module->get_data_pin(data_pin_num)->clear_buffer();
          break;
        case 'X': // Restart
          wireless_module->get_data_pin(data_pin_num)->start(true);
          break;
        case 'S': // Start
          wireless_module->get_data_pin(data_pin_num)->start(false);
          break;
        case 's': // Stop
          wireless_module->get_data_pin(data_pin_num)->stop();
          break;
        case 'U': // Send Updates Enabled
          wireless_module->get_data_pin(data_pin_num)->set_send_updates(true);
          break;
        case 'u': // Send Updates Disabled
          wireless_module->get_data_pin(data_pin_num)->set_send_updates(false);
          break;
        case 'O': // Toggle Output High On Read
          wireless_module->get_data_pin(data_pin_num)->set_output_high_on_read(true);
          break;
        case 'o': // Don't Toggle Output High On Read
          wireless_module->get_data_pin(data_pin_num)->set_output_high_on_read(false);
          break;
        case 'H': // Set Output High
          wireless_module->get_data_pin(data_pin_num)->set_output(PIN_ON);
          break;
        case 'L': // Set Output Low
          wireless_module->get_data_pin(data_pin_num)->set_output(PIN_OFF);
          break;
        default:
          break;
      }
    } else if (strcmp(arg_buff, "M") == 0) { // Module Info/Commands
      // Command
      arg_pos = extract_arg(arg_pos, arg_buff, arg_delims);
      char module_cmd = arg_buff[0];
      int pin_index;
      char send_buff[20];
      switch(module_cmd) {
        case 'R': // Reset
          // Stop data
          for (pin_index = 0; pin_index < NUM_INPUTS; pin_index++) {
            wireless_module->get_data_pin(pin_index)->stop();
          }

          // Stop LEDs
          for (pin_index = 0; pin_index < NUM_OUTPUTS; pin_index++) {
            wireless_module->get_led(pin_index)->stop();
          }

          // Set all pins to input
          for (pin_index = 0; pin_index < NUM_PAIRS; pin_index++) {
            wireless_module->get_pin(INPUT_PINS, pin_index)->set_mode(PM_INPUT);
            wireless_module->get_pin(OUTPUT_PINS, pin_index)->set_mode(PM_INPUT);
          }
          wireless_module->send_message("RReset");
          break;
        case 'D': // Disconnect
          Bluefruit.Advertising.restartOnDisconnect(false);
          Bluefruit.Advertising.stop();
          sd_ble_gap_disconnect(*(wireless_module->get_connection()),BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
          Bluefruit.Advertising.stop();
          break;
        case 'I': // Get ID
          sprintf(send_buff, "I%03d", MODULE_ID);
          wireless_module->send_message(send_buff);
          break;
        case 'V': // Get Version
          sprintf(send_buff, "V%s", MODULE_VERSION);
          wireless_module->send_message(send_buff);
          break;
        case 'N': // Get Name
          sprintf(send_buff, "NModule %s #%03d", MODULE_VERSION, MODULE_ID);
          wireless_module->send_message(send_buff);
          break;
        default:
          break;
      }
    }
    cmd_token = strtok(NULL, cmd_delim);
  }
}

void WirelessModule::send_message(char *message) {
    char update_buffer[40] = {0};
    sprintf(update_buffer, "%03dM%s", MODULE_ID, message);
    _bleuart->write(update_buffer, strlen(update_buffer));
}

/**
 * @brief Copies the first argument from str up to any character in delims into outs
 * 
 * @param str The char array to extract from
 * @param outs The char array to copy to
 * @param delims The chars to mark the end of an argument
 * @return char* A pointer to the position after the delimiter or NULL if str is empty
 * 
 * Why use this? As long as you keep track of the pointer, you can have multiple instances
 * of this running. This is useful, for example, when you want to simultaneously use strtok,
 * or just want to parse multiple strings at once
 * 
 * example usage:
 * 
 * char base_str[] = "Hello,this,1234,is,a,test";
 * char str_delims[] = ",";
 * 
 * char buff[40];
 * char *str_pos = base_str;
 * 
 * str_pos = extract_arg(str_pos, buff, str_delims);
 * while (str_pos != NULL) {
 *     printf("Extracted '%s'\n", buff);
 *     str_pos = extract_arg(str_pos, buff, str_delims);
 * }
 */
static char *extract_arg(char *str, char *outs, char *delims) {
  int delim_pos = strcspn(str, delims);
  snprintf(outs, delim_pos+1, "%s", str);
  return (delim_pos == 0 && str[0] == '\0') ? NULL : str+delim_pos+1;
}
