/*
 * ============================================================================
 * VR MODULE + MICRO-ROS - ESP32-C3
 * ============================================================================
 * Dual-mode firmware for the Elechouse Voice Recognition V3 module.
 *
 * MODE SELECTION — change the define below to switch modes:
 *
 *   #define VR_MODE TRAINING_MODE   → Serial command interface for training
 *   #define VR_MODE SENDING_MODE    → micro-ROS publisher for recognized voice
 *
 * WIRING (VR module → ESP32-C3):
 *   VR TX  → GPIO 3  (ESP32 RX)
 *   VR RX  → GPIO 4  (ESP32 TX)
 *
 * TRAINING MODE:
 *   Open Serial Monitor at 115200 baud and use commands:
 *     train 0 1 2          Train records 0, 1, 2
 *     load 0 1 2           Load records into recognizer
 *     sigtrain 0 FORWARD   Train record 0 with signature "FORWARD"
 *     vr                   Check recognizer status
 *     record               Check all record train status
 *     getsig 0             Get signature of record 0
 *     clear                Clear all records from recognizer
 *     settings             Check system settings
 *     help                 Print command list
 *
 * SENDING MODE (micro-ROS):
 *   Start the agent on your PC first:
 *     ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
 *   Publishes recognized voice record number to:
 *     Topic: /voice_command  (std_msgs/Int16)
 *   Node name: vr_microros_node
 * ============================================================================
 */

// ============================================================================
// MODE SELECTION — edit this line to switch modes
// ============================================================================
#define TRAINING_MODE 0
#define SENDING_MODE  1

#define VR_MODE SENDING_MODE   // <--- change to TRAINING_MODE to train

// ============================================================================
// COMMON INCLUDES
// ============================================================================
#include <Arduino.h>
#include "VoiceRecognitionV3.h"

// VR module software serial: RX=GPIO3, TX=GPIO4
VR myVR(4, 3);

// ============================================================================
// SHARED BUFFERS
// ============================================================================
uint8_t buf[255];

// ============================================================================
// ============================================================================
//
//   TRAINING MODE
//
// ============================================================================
// ============================================================================
#if VR_MODE == TRAINING_MODE

// --- Command parser defines -------------------------------------------------
#define CMD_BUF_LEN  65
#define CMD_NUM      10

typedef int (*cmd_function_t)(int, int);

uint8_t cmd[CMD_BUF_LEN];
uint8_t cmd_cnt;
uint8_t *paraAddr;
uint8_t records[7];

// Forward declarations
void printSeperator();
void printSignature(uint8_t *buf, int len);
void printVR(uint8_t *buf);
void printLoad(uint8_t *buf, uint8_t len);
void printTrain(uint8_t *buf, uint8_t len);
void printCheckRecognizer(uint8_t *buf);
void printUserGroup(uint8_t *buf, int len);
void printCheckRecord(uint8_t *buf, int num);
void printCheckRecordAll(uint8_t *buf, int num);
void printSigTrain(uint8_t *buf, uint8_t len);
void printSystemSettings(uint8_t *buf, int len);
void printHelp();
int receiveCMD();
int checkCMD(int len);
int checkParaNum(int len);
int findPara(int len, int paraNum, uint8_t **addr);
int compareCMD(uint8_t *para1, uint8_t *para2, int len);
int cmdTrain(int len, int paraNum);
int cmdLoad(int len, int paraNum);
int cmdTest(int len, int paraNum);
int cmdVR(int len, int paraNum);
int cmdClear(int len, int paraNum);
int cmdRecord(int len, int paraNum);
int cmdSigTrain(int len, int paraNum);
int cmdGetSig(int len, int paraNum);
int cmdSettings(int len, int paraNum);
int cmdHelp(int len, int paraNum);

const char cmdList[CMD_NUM][10] = {
  {"train"}, {"load"}, {"clear"}, {"vr"}, {"record"},
  {"sigtrain"}, {"getsig"}, {"Settings"}, {"test"}, {"help"},
};
const char cmdLen[CMD_NUM] = { 5, 4, 5, 2, 6, 8, 6, 8, 4, 4 };
cmd_function_t cmdFunction[CMD_NUM] = {
  cmdTrain, cmdLoad, cmdClear, cmdVR, cmdRecord,
  cmdSigTrain, cmdGetSig, cmdSettings, cmdTest, cmdHelp,
};

// ---------------------------------------------------------------------------
// SETUP — Training Mode
// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println(F("=== VR MODULE TRAINING MODE ==="));
  myVR.begin(9600);
  printSeperator();
  Serial.println(F("Usage:"));
  printSeperator();
  printHelp();
  printSeperator();
  cmd_cnt = 0;
}

// ---------------------------------------------------------------------------
// LOOP — Training Mode
// ---------------------------------------------------------------------------
void loop() {
  int len = receiveCMD();
  if (len > 0) {
    if (!checkCMD(len)) {
      int paraNum = checkParaNum(len);
      Serial.write(cmd, len);
      int paraLen = findPara(len, 1, &paraAddr);
      int i;
      for (i = 0; i < CMD_NUM; i++) {
        if (paraLen == cmdLen[i]) {
          if (compareCMD(paraAddr, (uint8_t *)cmdList[i], paraLen) == 0) {
            if (cmdFunction[i](len, paraNum) != 0) {
              printSeperator();
              Serial.println(F("Command Format Error!"));
              printSeperator();
            }
            break;
          }
        }
      }
      if (i == CMD_NUM) {
        printSeperator();
        Serial.println(F("Unknown command"));
        printSeperator();
      }
    } else {
      printSeperator();
      Serial.println(F("Command format error"));
      printSeperator();
    }
  }

  int ret = myVR.recognize(buf, 50);
  if (ret > 0) {
    printVR(buf);
  }
}

// ---------------------------------------------------------------------------
// Command receiver
// ---------------------------------------------------------------------------
int receiveCMD() {
  int ret, len;
  unsigned long start_millis = millis();
  while (1) {
    ret = Serial.read();
    if (ret > 0) {
      start_millis = millis();
      cmd[cmd_cnt] = ret;
      if (cmd[cmd_cnt] == '\n') {
        len = cmd_cnt + 1;
        cmd_cnt = 0;
        return len;
      }
      cmd_cnt++;
      if (cmd_cnt == CMD_BUF_LEN) { cmd_cnt = 0; return -1; }
    }
    if (millis() - start_millis > 100) { cmd_cnt = 0; return -1; }
  }
}

int compareCMD(uint8_t *para1, uint8_t *para2, int len) {
  for (int i = 0; i < len; i++) {
    uint8_t res = para2[i] - para1[i];
    if (res != 0 && res != 0x20) {
      res = para1[i] - para2[i];
      if (res != 0 && res != 0x20) return -1;
    }
  }
  return 0;
}

int checkCMD(int len) {
  for (int i = 0; i < len; i++) {
    if (cmd[i] > 0x1F && cmd[i] < 0x7F) {}
    else if (cmd[i] == '\t' || cmd[i] == ' ' || cmd[i] == '\r' || cmd[i] == '\n') {}
    else return -1;
  }
  return 0;
}

int checkParaNum(int len) {
  int cnt = 0, i = 0;
  while (i < len) {
    if (cmd[i] != '\t' && cmd[i] != ' ' && cmd[i] != '\r' && cmd[i] != '\n') {
      cnt++;
      while (i < len && cmd[i] != '\t' && cmd[i] != ' ' && cmd[i] != '\r' && cmd[i] != '\n') i++;
    } else i++;
  }
  return cnt;
}

int findPara(int len, int paraIndex, uint8_t **addr) {
  int cnt = 0, i = 0, paraLen;
  while (i < len) {
    uint8_t dt = cmd[i];
    if (dt != '\t' && dt != ' ') {
      cnt++;
      if (paraIndex == cnt) {
        *addr = cmd + i;
        paraLen = 0;
        while (i < len && cmd[i] != '\t' && cmd[i] != ' ' && cmd[i] != '\r' && cmd[i] != '\n') { i++; paraLen++; }
        return paraLen;
      } else {
        while (i < len && cmd[i] != '\t' && cmd[i] != ' ' && cmd[i] != '\r' && cmd[i] != '\n') i++;
      }
    } else i++;
  }
  return -1;
}

// ---------------------------------------------------------------------------
// Command handlers
// ---------------------------------------------------------------------------
int cmdHelp(int len, int paraNum) {
  if (paraNum != 1) return -1;
  printSeperator(); printHelp(); printSeperator();
  return 0;
}

int cmdTrain(int len, int paraNum) {
  if (paraNum < 2 || paraNum > 8) return -1;
  for (int i = 2; i <= paraNum; i++) {
    findPara(len, i, &paraAddr);
    records[i - 2] = atoi((char *)paraAddr);
    if (records[i - 2] == 0 && *paraAddr != '0') return -1;
  }
  printSeperator();
  int ret = myVR.train(records, paraNum - 1, buf);
  if (ret >= 0) printTrain(buf, ret);
  else if (ret == -1) Serial.println(F("Train failed."));
  else if (ret == -2) Serial.println(F("Train Timeout."));
  printSeperator();
  return 0;
}

int cmdLoad(int len, int paraNum) {
  if (paraNum < 2 || paraNum > 8) return -1;
  for (int i = 2; i <= paraNum; i++) {
    findPara(len, i, &paraAddr);
    records[i - 2] = atoi((char *)paraAddr);
    if (records[i - 2] == 0 && *paraAddr != '0') return -1;
  }
  int ret = myVR.load(records, paraNum - 1, buf);
  printSeperator();
  if (ret >= 0) printLoad(buf, ret);
  else Serial.println(F("Load failed or timeout."));
  printSeperator();
  return 0;
}

int cmdClear(int len, int paraNum) {
  if (paraNum != 1) return -1;
  printSeperator();
  if (myVR.clear() == 0) Serial.println(F("Recognizer cleared."));
  else Serial.println(F("Clear recognizer failed or timeout."));
  printSeperator();
  return 0;
}

int cmdVR(int len, int paraNum) {
  if (paraNum != 1) return -1;
  int ret = myVR.checkRecognizer(buf);
  printSeperator();
  if (ret <= 0) Serial.println(F("Check recognizer failed or timeout."));
  else printCheckRecognizer(buf);
  printSeperator();
  return 0;
}

int cmdRecord(int len, int paraNum) {
  printSeperator();
  if (paraNum == 1) {
    int ret = myVR.checkRecord(buf);
    if (ret >= 0) printCheckRecordAll(buf, ret);
    else Serial.println(F("Check record failed or timeout."));
  } else if (paraNum < 9) {
    for (int i = 2; i <= paraNum; i++) {
      findPara(len, i, &paraAddr);
      records[i - 2] = atoi((char *)paraAddr);
      if (records[i - 2] == 0 && *paraAddr != '0') return -1;
    }
    int ret = myVR.checkRecord(buf, records, paraNum - 1);
    if (ret >= 0) printCheckRecord(buf, ret);
    else Serial.println(F("Check record failed or timeout."));
  } else return -1;
  printSeperator();
  return 0;
}

int cmdSigTrain(int len, int paraNum) {
  if (paraNum < 2) return -1;
  findPara(len, 2, &paraAddr);
  records[0] = atoi((char *)paraAddr);
  if (records[0] == 0 && *paraAddr != '0') return -1;
  uint8_t *lastAddr;
  findPara(len, 3, &paraAddr);
  int sig_len = findPara(len, paraNum, &lastAddr);
  sig_len += ((unsigned int)lastAddr - (unsigned int)paraAddr);
  printSeperator();
  int ret = myVR.trainWithSignature(records[0], paraAddr, sig_len, buf);
  if (ret >= 0) printSigTrain(buf, ret);
  else Serial.println(F("Train with signature failed or timeout."));
  printSeperator();
  return 0;
}

int cmdGetSig(int len, int paraNum) {
  if (paraNum != 2) return -1;
  findPara(len, 2, &paraAddr);
  records[0] = atoi((char *)paraAddr);
  if (records[0] == 0 && *paraAddr != '0') return -1;
  int ret = myVR.checkSignature(records[0], buf);
  printSeperator();
  if (ret == 0) Serial.println(F("Signature isn't set."));
  else if (ret > 0) { Serial.print(F("Signature:")); printSignature(buf, ret); Serial.println(); }
  else Serial.println(F("Get sig error or timeout."));
  printSeperator();
  return 0;
}

int cmdTest(int len, int paraNum) {
  printSeperator();
  Serial.println(F("TEST is not supported."));
  printSeperator();
  return 0;
}

int cmdSettings(int len, int paraNum) {
  if (paraNum != 1) return -1;
  int ret = myVR.checkSystemSettings(buf);
  printSeperator();
  if (ret > 0) printSystemSettings(buf, ret);
  else Serial.println(F("Check system settings error or timeout"));
  printSeperator();
  return 0;
}

// ---------------------------------------------------------------------------
// Print helpers
// ---------------------------------------------------------------------------
void printSeperator() {
  for (int i = 0; i < 80; i++) Serial.write('-');
  Serial.println();
}

void printSignature(uint8_t *buf, int len) {
  for (int i = 0; i < len; i++) {
    if (buf[i] > 0x19 && buf[i] < 0x7F) Serial.write(buf[i]);
    else { Serial.print(F("[")); Serial.print(buf[i], HEX); Serial.print(F("]")); }
  }
}

void printVR(uint8_t *buf) {
  Serial.println(F("VR Index\tGroup\tRecordNum\tSignature"));
  Serial.print(buf[2], DEC); Serial.print(F("\t\t"));
  if (buf[0] == 0xFF) Serial.print(F("NONE"));
  else if (buf[0] & 0x80) { Serial.print(F("UG ")); Serial.print(buf[0] & (~0x80), DEC); }
  else { Serial.print(F("SG ")); Serial.print(buf[0], DEC); }
  Serial.print(F("\t")); Serial.print(buf[1], DEC); Serial.print(F("\t\t"));
  if (buf[3] > 0) printSignature(buf + 4, buf[3]);
  else Serial.print(F("NONE"));
  Serial.println(F("\r\n"));
}

void printCheckRecognizer(uint8_t *buf) {
  Serial.print(F("All voice records in recognizer: ")); Serial.println(buf[8], DEC);
  Serial.print(F("Valid voice records in recognizer: ")); Serial.println(buf[0], DEC);
  if (buf[10] == 0xFF) Serial.println(F("VR is not in group mode."));
  else if (buf[10] & 0x80) { Serial.print(F("VR is in user group mode:")); Serial.println(buf[10] & 0x7F, DEC); }
  else { Serial.print(F("VR is in system group mode:")); Serial.println(buf[10], DEC); }
  Serial.println(F("VR Index\tRecord\t\tComment"));
  for (int i = 0; i < 7; i++) {
    Serial.print(i, DEC); Serial.print(F("\t\t"));
    if (buf[i + 1] == 0xFF) {
      if (buf[10] == 0xFF) Serial.print(F("Unloaded\tNONE"));
      else Serial.print(F("Not Set\t\tNONE"));
    } else {
      Serial.print(buf[i + 1], DEC); Serial.print(F("\t\t"));
      Serial.print((buf[9] & (1 << i)) ? F("Valid") : F("Untrained"));
    }
    Serial.println();
  }
}

void printCheckRecord(uint8_t *buf, int num) {
  Serial.print(F("Check ")); Serial.print(buf[0], DEC); Serial.println(F(" records."));
  Serial.print(num, DEC); Serial.println(num > 1 ? F(" records trained.") : F(" record trained."));
  for (int i = 0; i < buf[0] * 2; i += 2) {
    Serial.print(buf[i + 1], DEC); Serial.print(F("\t-->\t"));
    switch (buf[i + 2]) {
      case 0x01: Serial.println(F("Trained")); break;
      case 0x00: Serial.println(F("Untrained")); break;
      case 0xFF: Serial.println(F("Record value out of range")); break;
      default:   Serial.println(F("Unknown Status")); break;
    }
  }
}

void printCheckRecordAll(uint8_t *buf, int num) {
  Serial.println(F("Check 255 records."));
  Serial.print(num, DEC); Serial.println(num > 1 ? F(" records trained.") : F(" record trained."));
  myVR.writehex(buf, 255);
  for (int i = 0; i < 255; i++) {
    if (buf[i] == 0xF0) continue;
    Serial.print(i, DEC); Serial.print(F("\t-->\t"));
    switch (buf[i]) {
      case 0x01: Serial.println(F("Trained")); break;
      case 0x00: Serial.println(F("Untrained")); break;
      case 0xFF: Serial.println(F("Record value out of range")); break;
      default:   Serial.println(F("Unknown Status")); break;
    }
  }
}

void printUserGroup(uint8_t *buf, int len) {
  Serial.println(F("Check User Group:"));
  for (int i = 0; i < len; i++) {
    Serial.print(F("Group:")); Serial.println(buf[8 * i]);
    for (int j = 0; j < 7; j++) {
      if (buf[8 * i + 1 + j] == 0xFF) Serial.print(F("NONE\t"));
      else { Serial.print(buf[8 * i + 1 + j], DEC); Serial.print(F("\t")); }
    }
    Serial.println();
  }
}

void printLoad(uint8_t *buf, uint8_t len) {
  if (len == 0) { Serial.println(F("Load Successfully.")); return; }
  Serial.print(F("Load success: ")); Serial.println(buf[0], DEC);
  for (int i = 0; i < len - 1; i += 2) {
    Serial.print(F("Record ")); Serial.print(buf[i + 1], DEC); Serial.print(F("\t"));
    switch (buf[i + 2]) {
      case 0:    Serial.println(F("Loaded")); break;
      case 0xFC: Serial.println(F("Record already in recognizer")); break;
      case 0xFD: Serial.println(F("Recognizer full")); break;
      case 0xFE: Serial.println(F("Record untrained")); break;
      case 0xFF: Serial.println(F("Value out of range")); break;
      default:   Serial.println(F("Unknown status")); break;
    }
  }
}

void printTrain(uint8_t *buf, uint8_t len) {
  if (len == 0) { Serial.println(F("Train Finish.")); return; }
  Serial.print(F("Train success: ")); Serial.println(buf[0], DEC);
  for (int i = 0; i < len - 1; i += 2) {
    Serial.print(F("Record ")); Serial.print(buf[i + 1], DEC); Serial.print(F("\t"));
    switch (buf[i + 2]) {
      case 0:    Serial.println(F("Trained")); break;
      case 0xFE: Serial.println(F("Train Time Out")); break;
      case 0xFF: Serial.println(F("Value out of range")); break;
      default:   Serial.print(F("Unknown status ")); Serial.println(buf[i + 2], HEX); break;
    }
  }
}

void printSigTrain(uint8_t *buf, uint8_t len) {
  if (len == 0) { Serial.println(F("Train With Signature Finish.")); return; }
  Serial.print(F("Success: ")); Serial.println(buf[0], DEC);
  Serial.print(F("Record ")); Serial.print(buf[1], DEC); Serial.print(F("\t"));
  switch (buf[2]) {
    case 0:    Serial.println(F("Trained")); break;
    case 0xF0: Serial.println(F("Trained, signature truncate")); break;
    case 0xFE: Serial.println(F("Train Time Out")); break;
    case 0xFF: Serial.println(F("Value out of range")); break;
    default:   Serial.print(F("Unknown status ")); Serial.println(buf[2], HEX); break;
  }
  Serial.print(F("SIG: ")); Serial.write(buf + 3, len - 3); Serial.println();
}

const unsigned int io_pw_tab[16] = { 10,15,20,25,30,35,40,45,50,75,100,200,300,400,500,1000 };

void printSystemSettings(uint8_t *buf, int len) {
  switch (buf[0]) {
    case 0: case 3: Serial.println(F("Baud rate: 9600")); break;
    case 1: Serial.println(F("Baud rate: 2400")); break;
    case 2: Serial.println(F("Baud rate: 4800")); break;
    case 4: Serial.println(F("Baud rate: 19200")); break;
    case 5: Serial.println(F("Baud rate: 38400")); break;
    default: Serial.println(F("Baud rate: UNKNOWN")); break;
  }
  switch (buf[1]) {
    case 0: case 0xFF: Serial.println(F("Output IO Mode: Pulse")); break;
    case 1: Serial.println(F("Output IO Mode: Toggle")); break;
    case 2: Serial.println(F("Output IO Mode: Clear (When recognized)")); break;
    case 3: Serial.println(F("Output IO Mode: Set (When recognized)")); break;
    default: Serial.println(F("Output IO Mode: UNKNOWN")); break;
  }
  if (buf[2] > 15) Serial.println(F("Pulse width: UNKNOWN"));
  else { Serial.print(F("Pulse Width: ")); Serial.print(io_pw_tab[buf[2]], DEC); Serial.println(F("ms")); }
  Serial.println((buf[3] == 0 || buf[3] == 0xFF) ? F("Auto Load: disable") : F("Auto Load: enable"));
  switch (buf[4]) {
    case 0: case 0xFF: Serial.println(F("Group control by external IO: disabled")); break;
    case 1: Serial.println(F("Group control by external IO: system group selected")); break;
    case 2: Serial.println(F("Group control by external IO: user group selected")); break;
    default: Serial.println(F("Group control by external IO: UNKNOWN")); break;
  }
}

void printHelp() {
  Serial.println(F("COMMAND        FORMAT                        EXAMPLE                    Comment"));
  printSeperator();
  Serial.println(F("train          train (r0) (r1)...            train 0 2 45               Train records"));
  Serial.println(F("load           load (r0) (r1) ...            load 0 51 2 3              Load records"));
  Serial.println(F("clear          clear                         clear                      Remove all records from Recognizer"));
  Serial.println(F("record         record / record (r0) (r1)...  record / record 0 79       Check record train status"));
  Serial.println(F("vr             vr                            vr                         Check recognizer status"));
  Serial.println(F("getsig         getsig (r)                    getsig 0                   Get signature of record (r)"));
  Serial.println(F("sigtrain       sigtrain (r) (sig)            sigtrain 0 FORWARD         Train one record with signature"));
  Serial.println(F("settings       settings                      settings                   Check current system settings"));
  Serial.println(F("help           help                          help                       Print this message"));
}

// ============================================================================
// ============================================================================
//
//   SENDING MODE  (micro-ROS)
//
// ============================================================================
// ============================================================================
#elif VR_MODE == SENDING_MODE

#include <micro_ros_platformio.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int16.h>
#include <std_msgs/msg/string.h>

#if !defined(MICRO_ROS_TRANSPORT_ARDUINO_SERIAL)
#error This firmware requires Arduino framework with serial transport.
#endif

// ============================================================================
// CONFIGURATION
// ============================================================================

// Node and topic names
#define NODE_NAME          "vr_microros_node"
#define VOICE_TOPIC        "voice_command"

// Records to load into the VR recognizer on boot (adjust to match your training)
// These are the record slots you trained, e.g. 0=FORWARD, 1=BACK, 2=LEFT, 3=RIGHT
#define VR_RECORD_COUNT    4
static uint8_t vrRecords[VR_RECORD_COUNT] = { 0, 1, 2, 3 };

// Status LED pin (ESP32-C3 built-in LED is GPIO 8 on most devkits)
#define STATUS_LED_PIN     8

// ============================================================================
// MICRO-ROS OBJECTS
// ============================================================================

// Publisher: sends recognized voice record number on /voice_command
rcl_publisher_t voice_publisher;
std_msgs__msg__Int16 voice_msg;

rclc_executor_t executor;
rclc_support_t  support;
rcl_allocator_t allocator;
rcl_node_t      node;
rcl_timer_t     timer;

// ============================================================================
// ERROR MACROS
// ============================================================================
#define RCCHECK(fn)     { rcl_ret_t rc = fn; if (rc != RCL_RET_OK) { error_loop(); } }
#define RCSOFTCHECK(fn) { rcl_ret_t rc = fn; (void)rc; }

// ============================================================================
// ERROR LOOP
// ============================================================================
void error_loop() {
  Serial.println(F("[ERROR] micro-ROS init failed. Check agent connection. Restarting..."));
  for (int i = 0; i < 20; i++) {
    digitalWrite(STATUS_LED_PIN, i % 2);
    delay(100);
  }
  ESP.restart();
}

// ============================================================================
// TIMER CALLBACK — polls VR module and publishes recognized command
// ============================================================================
void timer_callback(rcl_timer_t *timer, int64_t last_call_time) {
  RCLC_UNUSED(last_call_time);
  if (timer == NULL) return;

  int ret = myVR.recognize(buf, 50);
  if (ret > 0) {
    // buf[1] = record number that was recognized
    int16_t recordNum = (int16_t)buf[1];
    voice_msg.data = recordNum;

    RCSOFTCHECK(rcl_publish(&voice_publisher, &voice_msg, NULL));

    Serial.printf("[VR] Recognized record: %d  (VR index: %d)\n", recordNum, buf[2]);

    // Optional: print signature if present
    if (buf[3] > 0) {
      Serial.print(F("[VR] Signature: "));
      for (int i = 0; i < buf[3]; i++) {
        if (buf[4 + i] > 0x19 && buf[4 + i] < 0x7F) Serial.write(buf[4 + i]);
      }
      Serial.println();
    }
  }
}

// ============================================================================
// SETUP — Sending Mode
// ============================================================================
void setup() {
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, HIGH);  // LED on during init

  Serial.begin(115200);
  delay(2000);

  Serial.println(F("\n=== VR MODULE SENDING MODE (micro-ROS) ==="));
  Serial.println(F("Node:    " NODE_NAME));
  Serial.println(F("Topic:   /voice_command  (std_msgs/Int16)"));

  // --- Init VR module ---
  myVR.begin(9600);
  Serial.println(F("\nLoading VR records into recognizer..."));
  int loadRet = myVR.load(vrRecords, VR_RECORD_COUNT, buf);
  if (loadRet >= 0) {
    Serial.printf("Loaded %d records successfully.\n", loadRet);
  } else {
    Serial.println(F("[WARN] VR load failed or timed out. Check wiring."));
  }

  // --- micro-ROS setup ---
  set_microros_serial_transports(Serial);
  delay(500);

  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, NODE_NAME, "", &support));

  // Publisher: /voice_command  Int16
  RCCHECK(rclc_publisher_init_default(
    &voice_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int16),
    VOICE_TOPIC));

  // Timer: polls VR module every 100 ms
  RCCHECK(rclc_timer_init_default2(
    &timer, &support,
    RCL_MS_TO_NS(100),
    timer_callback,
    true));

  // Executor: 1 handle (timer only)
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_timer(&executor, &timer));

  digitalWrite(STATUS_LED_PIN, LOW);  // LED off = ready
  Serial.println(F("\n✓ Ready. Listening for voice commands...\n"));
}

// ============================================================================
// LOOP — Sending Mode
// ============================================================================
void loop() {
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
  delay(10);
}

#endif // VR_MODE
