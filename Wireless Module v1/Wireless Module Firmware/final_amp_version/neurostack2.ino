/* BLE Example for SparkFun Pro nRF52840 Mini 
 *  
 *  This example demonstrates how to use the Bluefruit
 *  library to both send and receive data to the
 *  nRF52840 via BLE.
 *  
 *  Using a BLE development app like Nordic's nRF Connect
 *  https://www.nordicsemi.com/eng/Products/Nordic-mobile-Apps/nRF-Connect-for-Mobile
 *  The BLE UART service can be written to to turn the
 *  on-board LED on/off, or read from to monitor the 
 *  status of the button.
 *  
 *  See the tutorial for more information:
 *  https://learn.sparkfun.com/tutorials/nrf52840-development-with-arduino-and-circuitpython#arduino-examples  
*/
#include <bluefruit.h>
#include <Arduino.h>
#include <nrf_saadc.h>

BLEUart bleuart; // uart over ble

// Define hardware: LED and Button pins and states
//These are for NRF52832v9 (Temp sensing 2-LED with optional DAC control)
const int LED_PIN1 = 14;
const int LED_PIN2 = 8; //WARNING: THIS IS THE SAME AS LDO_OUT MAKE SURE THEY ARE NEVER ON AT THE SAME TIME
const int DAC_CS = 11;
const int DAC_DIN = 28;
const int DAC_SCLK = 2;
const int LDO_IN = 12;
const int LDO_EN = 6;


#define LED_OFF LOW
#define LED_ON HIGH
#define OFF 0
#define ON 1

// Initialize global state variables
int session_timer;
int session_state;
int pulse_state;
int pulse_timer;
int wave_state;
int wave_timer;
int first8 = 156;
int second8 = 128;
uint16_t connection;
int clock_break = 0;
short int tempvoltages[100];
short int ampvoltages[100];
int i = 0;
int j = 0;
bool count_up;
bool count_down;

// Initialize Parameters to be obtained from central
int pulse_width;
int valley_width;
int on_period;
int off_period;
int led_pin;
int disconnect_after_start = 1;
int max_val = 255;
int num_steps = 28;
int rise_time;
int fall_time;
int temp_sample;
int temp_period;
int record_sample;
int record_period;

SoftwareTimer longtimer;
SoftwareTimer shorttimer;
SoftwareTimer temptimer;
SoftwareTimer recordtimer;

void setup() {
  // Initialize hardware:

  //Disable everything to save power (except the ADC because we are using that)
  NRF_UARTE0->ENABLE = 0;  //disable UART
  NRF_SAADC ->ENABLE = 1; //disable ADC
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

  //Turn on oversampling to reduce ADC noise
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
  Bluefruit.setTxPower(-4);
  Bluefruit.setName("SparkFun_nRF52840");
  Bluefruit.Periph.setConnectCallback(prph_connect_callback);
  bleuart.begin();

  // Start advertising device and bleuart services
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(bleuart);
  Bluefruit.ScanResponse.addName();

  // Set advertising interval (in unit of 0.625ms):
  Bluefruit.Advertising.setInterval(1500,1600);
  // number of seconds in fast mode:
  Bluefruit.Advertising.setFastTimeout(0);
  Bluefruit.Advertising.start(0);

  //Initialize Global Parameters
  clock_break = 0;  
  i = 0;
  num_steps = 28;
  //Set needed sampling resolutioon
  analogReadResolution(14);
}

void loop() {
  //Count down controls the fall time (only used for when DAC board is attached)
  if (count_down){
    falltime();
  }
  // Count up controls the rise time based on given values (only used for when DAC board is attached)
  if (count_up){
    risetime();
  }
  if (bleuart.available()) {
    //If a new instruction is recieved pause everything
    digitalWrite(LED_PIN1, LED_OFF);
    digitalWrite(LED_PIN2, LED_OFF);
    longtimer.stop();
    shorttimer.stop();
    if (temp_sample == 1){
        temptimer.stop();
        //digitalWrite(LDO_IN, LOW); 
        digitalWrite(LDO_EN, LOW);
      }
        if (record_sample == 1){
        digitalWrite(DAC_SCLK, LOW);
      }
    if (led_pin == 3){
      digitalWrite(DAC_CS, LED_OFF);
      digitalWrite(DAC_DIN, LED_OFF);
      digitalWrite(DAC_SCLK, LED_OFF);
      shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,0b11100000);
      shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,0b00000000);
      digitalWrite(DAC_CS, LED_ON);
    }

    uint8_t c;
    char output[80];
    // use bleuart.read() to read a character sent over BLE
    bleuart.read(output, 80);
    if (strlen(output) > 10){
      extract(output);
      //Config LEDs based on settings
      configleds();
      //Reset all of the wave timers
      resetpulses();

      //Initialize timer periods
      longtimer.begin(1000, long_timer_callback);
      shorttimer.begin(clock_break, short_timer_callback);
      if (temp_sample == 1){
        temptimer.begin(temp_period, temp_timer_callback);
      }
      if (record_sample == 1){
        recordtimer.begin(record_period, record_timer_callback);
      }

      //Begin timers
      longtimer.start();
      shorttimer.start();
      if (temp_sample == 1){
        temptimer.start();
      }
      if (record_sample == 1){
        recordtimer.start();
      }
    }
  }
   //If temp data has filled the buffer, send all data at once
   if (i>=100){
    bleuart.write((byte*) tempvoltages, sizeof(tempvoltages));
    i = 0;
   }
   //If recording data has filled the buffer, send all data at once
   if (j>=100){
    bleuart.write((byte*) ampvoltages, sizeof(ampvoltages));
    j = 0;
   }
  sd_app_evt_wait();
}

void extract(char* data_array){
  const char s[2] = ",";
  char *token;
  token = strtok(data_array, s);
  char buff[30] = {0};
  int token_num = 0;
  while( token != NULL ) {
      sprintf(buff, "%s\n", token );
      char temp[30]={0};
      switch(token_num){
        case 0:
          strcpy(temp, buff);
          pulse_width = atoi(temp);
          break;
        case 1:
          strcpy(temp, buff);
          valley_width = atoi(temp);
          break;  
        case 2:
          strcpy(temp, buff);
          on_period = atoi(temp);
          break;
        case 3:
          strcpy(temp, buff);
          off_period = atoi(temp);
          break;
        case 4: 
          strcpy(temp, buff);
          led_pin = atoi(temp);
          break;
        case 5:
          strcpy(temp, buff);
          disconnect_after_start = atoi(temp);
          break;
        case 6:
          strcpy(temp, buff);
          temp_sample = atoi(temp);
          break;
        case 7:
          strcpy(temp, buff);
          temp_period = atoi(temp);
          break;
        case 8:
          strcpy(temp, buff);
          record_sample = atoi(temp);
          break;
        case 9:
          strcpy(temp, buff);
          record_period = atoi(temp);
          break;
        case 10:
          strcpy(temp, buff);
          max_val = atoi(temp);
          break;
        case 11:
          strcpy(temp, buff);
          rise_time = atoi(temp);
          break;
        case 12:
          strcpy(temp, buff);
          fall_time = atoi(temp);
          break;
//        case 13:
//          strcpy(temp, buff);
//          num_steps = atoi(temp);
//          break;
      }
      token = strtok(NULL, s);
      token_num++;
   }
   //reduce short clock to gcd of the two periods
   clock_break = gcd(pulse_width, valley_width);
   //rescale counters based on gcd
   pulse_width = pulse_width/clock_break;
   valley_width = valley_width/clock_break;
}

void prph_connect_callback(uint16_t conn_handle){
    connection = conn_handle;
}

int gcd(int a, int b)
{
    int temp;
    while (b != 0)
    {
        temp = a % b;

        a = b;
        b = temp;
    }
    return a;
}

void configleds(){
   if (led_pin == 1 ){
    pinMode(LED_PIN1, OUTPUT); 
    digitalWrite(LED_PIN1, LED_OFF);
   }
   if (led_pin == 2){
    pinMode(LED_PIN2, OUTPUT);
    digitalWrite(LED_PIN2, LED_OFF);
   }
   if (led_pin == 3){
    //Enable DAC usage if selected
    pinMode(8, OUTPUT);
    pinMode(DAC_DIN, OUTPUT);
    pinMode(DAC_SCLK, OUTPUT);
    pinMode(DAC_CS, OUTPUT);
    digitalWrite(DAC_CS, LED_ON);
    digitalWrite(DAC_DIN, LED_OFF);
    digitalWrite(DAC_SCLK, LED_OFF);
   }
   if (led_pin == 4){
    pinMode(LED_PIN2, OUTPUT);
    digitalWrite(LED_PIN2, LED_OFF);
    pinMode(LED_PIN1, OUTPUT); 
    digitalWrite(LED_PIN1, LED_OFF);
   }
   if (led_pin != 2 || led_pin != 4){
     if (temp_sample == 1){
    //Enable LDO for temp sensing if not using LED2
      pinMode(LDO_IN, OUTPUT); 
      digitalWrite(LDO_IN, HIGH);
      pinMode(LDO_EN, OUTPUT); 
      digitalWrite(LDO_EN, HIGH);
    }
   }
      if (record_sample == 1){
      pinMode(DAC_SCLK, OUTPUT); // SCLK is used as SHDN pin
      digitalWrite(DAC_SCLK, LED_ON); //set SHDN to HIGH
      pinMode(DAC_DIN, INPUT); // amplifier VIN
      pinMode(DAC_CS, INPUT); // amplifier VBODY
   }

  if (disconnect_after_start == 1){
    //If constant communication isn't necessary, you can disconnect upon recieving instructions
    Bluefruit.Advertising.restartOnDisconnect(false);
    Bluefruit.Advertising.stop();
    sd_ble_gap_disconnect(connection,BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
    Bluefruit.Advertising.stop();  
  }
}
void falltime(){
  int val = max_val;
  int num_steps = 28;
  int step_size = val/num_steps;
  int remainder = max_val%num_steps;
  int step_num = 0;
  while(step_num < num_steps+1){
    first8 = ( 0b10010000 | (val & 0xF0) >> 4  );
    second8 = ( (val & 0x0F) << 4 | 0b0000);
    digitalWrite(DAC_CS, LED_OFF);
    digitalWrite(DAC_DIN, LED_OFF);
    digitalWrite(DAC_SCLK, LED_OFF);
    shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,first8);
    shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,second8);
    digitalWrite(DAC_CS, LED_ON);
    delayMicroseconds(fall_time);
    step_num++;
    val = val - step_size;
    if (step_num < remainder){
      val = val - 1;
    }
  }
  val = 0;
  first8 = ( 0b10010000 | (val & 0xF0) >> 4  );
  second8 = ( (val & 0x0F) << 4 | 0b0000);
  digitalWrite(DAC_CS, LED_OFF);
  digitalWrite(DAC_DIN, LED_OFF);
  digitalWrite(DAC_SCLK, LED_OFF);
  shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,first8);
  shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,second8);
  digitalWrite(DAC_CS, LED_ON);
  wave_state = OFF;
  wave_timer = 0;
  count_down = false;
}

void risetime(){
  int val = 0;
  int num_steps = 28;
  int step_size = max_val/num_steps;
  int remainder = max_val%num_steps;
  int step_num = 0;
  while(step_num < num_steps){
    first8 = ( 0b10010000 | (val & 0xF0) >> 4  );
    second8 = ( (val & 0x0F) << 4 | 0b0000);
    digitalWrite(DAC_CS, LED_OFF);
    digitalWrite(DAC_DIN, LED_OFF);
    digitalWrite(DAC_SCLK, LED_OFF);
    shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,first8);
    shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,second8);
    digitalWrite(DAC_CS, LED_ON);
    delayMicroseconds(rise_time);
    step_num++;
    val = val + step_size;
    if (step_num < remainder){
      val = val + 1;
    }
  }
  val = max_val;
  first8 = ( 0b10010000 | (val & 0xF0) >> 4  );
  second8 = ( (val & 0x0F) << 4 | 0b0000);
  digitalWrite(DAC_CS, LED_OFF);
  digitalWrite(DAC_DIN, LED_OFF);
  digitalWrite(DAC_SCLK, LED_OFF);
  shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,first8);
  shiftOut(DAC_DIN, DAC_SCLK, MSBFIRST,second8);
  digitalWrite(DAC_CS, LED_ON);
  wave_state = ON;
  wave_timer = 0;
  count_up = false;
}

void resetpulses(){
  session_timer = 0;
  session_state = ON;
  pulse_state = ON;
  pulse_timer = 0;
  wave_state = OFF;
  wave_timer = 0;
}

void long_timer_callback(TimerHandle_t xTimerID1){//timer1 interrupt 1Hz toggles pin 13 (LED)
//generates pulse wave of frequency 1Hz/2 = 0.5kHz (takes two cycles for full wave- toggle high then toggle low)
  (void) xTimerID1;
  //This is for killing the session after a certain period of time (1800 is 30 minutes)
//  session_timer++;
//  if (session_timer >= 1800){
//      if (led_pin == 1){
//        digitalWrite(LED_PIN1, LED_OFF);
//      }
//       if (led_pin == 2) {
//        digitalWrite(LED_PIN2, LED_OFF);
//      }
////      if (indicator == 1){
////        digitalWrite(LED_PIN3, LED_OFF);
//////       }
////      if (led_pin == 3){
////        count_down = true; 
////      }
//      session_state = OFF;
//  }
//  
  pulse_timer++;
  if (pulse_state==OFF && pulse_timer>=off_period){
    pulse_state = ON;
    pulse_timer = 0;
    shorttimer.start();

    //Don't start wave timer until rise_time is over 
    if (led_pin == 3){
        count_up = true; 
        return;
    }
    wave_state = ON;
    wave_timer = 0;
    if (led_pin == 1 || led_pin == 4){
        digitalWrite(LED_PIN1, LED_ON);
    }
    if (led_pin == 2 || led_pin == 4) {
        digitalWrite(LED_PIN2, LED_ON);
    }
  }
  else if (pulse_state == ON && pulse_timer>=on_period){
    pulse_state = OFF;
    pulse_timer = 0;
    if (led_pin == 1 || led_pin == 4){
      digitalWrite(LED_PIN1, LED_OFF);
    }
     if (led_pin == 2 || led_pin == 4) {
      digitalWrite(LED_PIN2, LED_OFF);
    }
    if (led_pin == 3){
        count_down = true;
    }
    //Stop short timer to save power
    shorttimer.stop();
  }
}


void short_timer_callback(TimerHandle_t xTimerID2){//timer0 interrupt 1kHz toggles pin 8
//generates pulse wave of frequency 2kHz/2 = 1kHz (takes two cycles for full wave- toggle high then toggle low)
  (void) xTimerID2;
  if (count_down == false && count_up == false){
    wave_timer++;
  }
  if (pulse_state==ON){
    if (wave_state == ON && wave_timer >= pulse_width){
       if (led_pin == 1 || led_pin == 4){
        digitalWrite(LED_PIN1, LED_OFF);
      }
      if (led_pin == 2 || led_pin == 4) {
        digitalWrite(LED_PIN2, LED_OFF);
      }
      if (led_pin == 3){
        count_down = true; 
      }
      wave_state = OFF;
      wave_timer = 0;
    }
    else if (wave_state == OFF && wave_timer >= valley_width){
      if (led_pin == 3){
        count_up = true; 
      }
       if (led_pin == 1 || led_pin == 4){
        digitalWrite(LED_PIN1, LED_ON);
      }
       if (led_pin == 2 || led_pin == 4) {
        digitalWrite(LED_PIN2, LED_ON);
      }
      wave_state = ON;
      wave_timer = 0;
    }
  }
}

void temp_timer_callback(TimerHandle_t xTimerID3){
  (void) xTimerID3;
    tempvoltages[i] = analogRead(A6);
    i++;
}
void record_timer_callback(TimerHandle_t xTimerID5){
  (void) xTimerID5;
    ampvoltages[j] = analogRead(DAC_DIN);
    j++;
}
