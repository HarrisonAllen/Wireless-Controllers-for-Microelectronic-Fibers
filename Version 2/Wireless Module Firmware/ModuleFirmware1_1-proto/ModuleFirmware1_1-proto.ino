#include <bluefruit.h>
#include "WirelessModule.h"
#include "MiscDefines.h"
#include <nrf_saadc.h>
#include <nrf_gpio.h>

BLEUart bleuart;

// For bluetooth callback
uint16_t connection;

// Set up pins
Pin pin_in_0(INPUT_PIN_NUMS[0], INPUT_PIN_ID * NUM_PAIRS + 0, &bleuart);
Pin pin_in_1(INPUT_PIN_NUMS[1], INPUT_PIN_ID * NUM_PAIRS + 1, &bleuart);
Pin pin_in_2(INPUT_PIN_NUMS[2], INPUT_PIN_ID * NUM_PAIRS + 2, &bleuart);
Pin pin_in_3(INPUT_PIN_NUMS[3], INPUT_PIN_ID * NUM_PAIRS + 3, &bleuart);
Pin pin_out_0(OUTPUT_PIN_NUMS[0], OUTPUT_PIN_ID * NUM_PAIRS + 0, &bleuart);
Pin pin_out_1(OUTPUT_PIN_NUMS[1], OUTPUT_PIN_ID * NUM_PAIRS + 1, &bleuart);
Pin pin_out_2(OUTPUT_PIN_NUMS[2], OUTPUT_PIN_ID * NUM_PAIRS + 2, &bleuart);
Pin pin_out_3(OUTPUT_PIN_NUMS[3], OUTPUT_PIN_ID * NUM_PAIRS + 3, &bleuart);
Pin *pins[NUM_PINS] = {&pin_in_0, &pin_in_1, &pin_in_2, &pin_in_3, &pin_out_0, &pin_out_1, &pin_out_2, &pin_out_3};

// Preallocate LEDs
LED led_0(&pin_out_0, &bleuart);
LED led_1(&pin_out_1, &bleuart);
LED led_2(&pin_out_2, &bleuart);
LED led_3(&pin_out_3, &bleuart);
LED *leds[NUM_OUTPUTS] = {&led_0, &led_1, &led_2, &led_3};

// Preallocate Data PIns
DataPin data_pin_0(&pin_in_0, &pin_out_0, &bleuart);
DataPin data_pin_1(&pin_in_1, &pin_out_1, &bleuart);
DataPin data_pin_2(&pin_in_2, &pin_out_2, &bleuart);
DataPin data_pin_3(&pin_in_3, &pin_out_3, &bleuart);
DataPin *data_pins[NUM_INPUTS] = {&data_pin_0, &data_pin_1, &data_pin_2, &data_pin_3};


WirelessModule wireless_module(&pins, &leds, &data_pins, &bleuart, &connection);

void setup() {
  //Disable everything to save power (except the ADC because we are using that)
  NRF_UARTE0->ENABLE = 0;  //disable UART
  //  NRF_SAADC ->ENABLE = 0; //disable ADC
  NRF_PWM0  ->ENABLE = 0; //disable all pwm instance
  NRF_PWM1  ->ENABLE = 0;
  NRF_PWM2  ->ENABLE = 0;
  NRF_TWIM1 ->ENABLE = 0; //disable TWI Master
  NRF_TWIS1 ->ENABLE = 0; //disable TWI Slave
  NRF_TWIM0 ->ENABLE = 0; //disable TWI Master
  NRF_TWIS0 ->ENABLE = 0; //disable TWI Slave
  NRF_I2S -> ENABLE = 0;
  NRF_PDM -> ENABLE = 0;
  NRF_SPI0 -> ENABLE = 0; //disable SPI
  NRF_SPI1 -> ENABLE = 0; //disable SPI
  NRF_SPI2 -> ENABLE = 0; //disable SPI
  NRF_POWER -> DCDCEN = 0x00000001;

  //Turn on oversasdmpling to reduce ADC noise
  analogOversampling(128);

  //Enable low power mode
  sd_power_mode_set(NRF_POWER_MODE_LOWPWR);

  //Set connection parameters: Most relevant is the first number which is packet size
  Bluefruit.configPrphConn(244, 3, 2, BLE_GATTC_WRITE_CMD_TX_QUEUE_SIZE_DEFAULT);

  // Uncomment the code below to disable sharing the connection LED on pin 7.
  Bluefruit.autoConnLed(false);

  // Initialize Bluetooth:
  Bluefruit.begin();
  // Set max power. Accepted values are: -40, -30, -20, -16, -12, -8, -4, 0, 4
  Bluefruit.setTxPower(4);
  char bt_name_buffer[40];
  sprintf(bt_name_buffer, "Module %s #%03d", MODULE_VERSION, MODULE_ID);
  Bluefruit.setName(bt_name_buffer);
  Bluefruit.Periph.setConnectCallback(prph_connect_callback);
  bleuart.begin();

  // Start advertising device and bleuart services
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(bleuart);
  Bluefruit.ScanResponse.addName();

  // Set advertising interval (in unit of 0.625ms):
  Bluefruit.Advertising.setInterval(1500, 1600);
  // number of seconds in fast mode:
  Bluefruit.Advertising.setFastTimeout(0);
  Bluefruit.Advertising.start(0);

  analogReadResolution(14);
}

void loop() {
  if (bleuart.available()) {
    char data[200];
    bleuart.read(data, 200);
    wireless_module.handle_data(data);
  }
  sd_app_evt_wait();
}

void prph_connect_callback(uint16_t conn_handle) {
  connection = conn_handle;
}
