# Micro-ROS Template voor ESP32 (PlatformIO)

Een volledig functionele **micro-ROS template** voor ESP32 met publisher, subscriber en seriële transport.

---

## 📋 Inhoudsopgave

- [Projectbeschrijving](#projectbeschrijving)
- [Hardware Vereisten](#hardware-vereisten)
- [Software Vereisten](#software-vereisten)
- [Installatie](#installatie)
- [Hoe het Werkt](#hoe-het-werkt)
- [ROS 2 Commando's](#ros-2-commando's)
- [Onderwerpen Gebruiken](#onderwerpen-gebruiken)
- [Aanpassingen voor Jouw Sensoren & Actuatoren](#aanpassingen-voor-jouw-sensoren--actuatoren)
- [Troubleshooting](#troubleshooting)
- [Project Structuur](#project-structuur)

---

## Projectbeschrijving

Dit project implementeert een **micro-ROS node** op ESP32 met:

- **Publisher** (`template_publisher`) — Verzendt Int16 sensordata elke 1 seconde
- **Subscriber** (`template_subscriber`) — Ontvangt Float32 reactiecommando's van ROS 2
- **Timer-gebaseerde callbacks** — Periodieke sensormeting op 1 Hz
- **Event-gebaseerde callbacks** — Onmiddellijke reactie op inkomende berichten
- **Foutafhandeling** — LED-feedback en veilige hertart op kritische fouten
- **Seriële Transport** — Communicatie via USB naar micro-ROS agent op host-PC

### Diagram: ROS 2 Netwerk

```
┌─────────────────────────────────────────┐
│       ROS 2 Host (Linux/macOS/Windows)  │
│                                         │
│  ros2 topic pub/sub                     │
│  ros2 topic echo /template_publisher    │
│  ros2 topic pub /template_subscriber    │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ micro_ros_agent serial --dev /dev/.. ││
│  └─────────────────────────────────────┘│
└──────────────┬──────────────────────────┘
               │ USB/Serial (115200 baud)
               │
┌──────────────┴──────────────────────────┐
│           ESP32 Dev Board                │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Micro-ROS Node: "microros_temp.."  │ │
│  │                                    │ │
│  │  Publisher ──➜ /template_publisher│ │
│  │            (Int16, 1 Hz)           │ │
│  │                                    │ │
│  │  Subscriber ◀── /template_subscriber│
│  │             (Float32, event-driven) │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  📍 Hardware:                            │
│     • Status LED (GPIO PIN: platformio.ini)
│     • Sensoren (✏️ TODO: jij!)           │
│     • Actuatoren (✏️ TODO: jij!)         │
│                                          │
└──────────────────────────────────────────┘
```

---

## Hardware Vereisten

### Microcontroller (kies een van beiden)

| Option | Board | Baudrate | Status LED |
|--------|-------|----------|------------|
| **Option 1** | ESP32-C3 DevKitM-1 | 115200 | GPIO 8 |
| **Option 2** | UPESY WROOM | 115200 | GPIO 2 |

### Verdere Items

- **USB-A naar Micro-USB kabel** — Voor seriële communicatie
- **Development machine** — Linux, macOS, of Windows met ROS 2 Humble/Iron

### Optioneel (voor sensoren/actuatoren)

- **Jumper wires** — Voor GPIO-aansluiting
- **Breadboard** — Voor prototying
- **Sensoren**: DHT22, Ultrasonic, LDR, ADC sensors, etc.
- **Actuatoren**: LED's, servo's, relais, motoren, etc.

---

## Software Vereisten

### Geïnstalleerd op ESP32 (via PlatformIO)

- **Arduino Framework** — Compatibiliteit met Arduino API
- **micro_ros_platformio** — Micro-ROS bibliotheek
- **std_msgs** — ROS 2 standaard berichttypes

### Geïnstalleerd op Host-PC

- **ROS 2** (Humble of hoger) — Full ROS 2 stack
- **micro-ROS Agent** — Voor seriële communicatie met ESP32

  ```bash
  # Installatie micro-ROS Agent
  sudo apt install ros-jazzy-micro-ros-agent
  ```

- **PlatformIO CLI** (optioneel, VS Code extension werkt ook)

---

## Installatie

### 1. Repository Clonen

```bash
git clone https://github.com/AvansMechatronica/microros_template
cd microros_template
```

### 2. PlatformIO Build Environment

VS Code plugin: **PlatformIO IDE**

```bash
# Of via CLI:
platformio platform install espressif32
platformio lib install micro_ros_platformio
```

### 3. USB-kabel Aansluiten

Sluit je ESP32 aan op je development machine via USB.

**Kom je USB-poort op?**

```bash
# Linux/macOS
ls /dev/ttyUSB* /dev/ttyACM*


```

### 4. Board Selecteren

In [`platformio.ini`](platformio.ini):

```ini
[platformio]
default_envs = esp32-C3    # of: eps32-upesy_wroom
```

### 5. Code Compileren & Flashen

```bash
# Via PlatformIO VS Code:
# - Klik "PlatformIO: Build"
# - Klik "PlatformIO: Upload"

# Of via CLI:
platformio run
platformio run --target upload
```

### Stap 6: Micro-ROS Agent Starten (op Host-PC)

In een **nieuwe terminal** op je Linux/macOS machine:

```bash
# Vervang /dev/ttyUSB0 met je eigen USB-poort
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

Verwachte output:
```
...
[INFO] Trying to connect to /dev/ttyUSB0 at 115200 baud.
[INFO] Micro-ROS Agent has been set up successfully on port /dev/ttyUSB0 with baudrate 115200.
[INFO] Waiting for subscribers...
```

### Stap 7: ROS 2 Topics Controleren

In een **derde terminal**:

```bash
# Zie alle topics
ros2 topic list
# Verwacht:
#   /microros_template_node/parameter_events
#   /rosout
#   /template_publisher
#   /template_subscriber

# Zie alle nodes
ros2 node list
# Verwacht:
#   /microros_template_node
#   /rostopic_...
```

### Stap 8: Publisher Data Ontvangen

```bash
ros2 topic echo /template_publisher
```

Je ziet elke seconde:
```
data: 42
---
data: 42
---
```

### Stap 9: Subscriber Data Versturen

In een **vierde terminal**:

```bash
# Verstuur willekeurige Float32 waarde
ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 3.14}"
```

Controleer je seriële monitor:
```
[SUBSCRIBER] Ontvangen Float32: 3.14
```

---

## Hoe het Werkt

### Architectuur: Executor Pattern

```
┌─────────────────────┐
│   loop() draait      │  Oneindige lus @ 100 ms
│   elke 100 ms       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ rclc_executor_spin_some():              │
│ Controleer alle geregistreerde callbacks│
└──────────┬──────────────────────────────┘
           │
      ┌────┴────┐
      │          │
      ▼          ▼
  ┌────────┐  ┌──────────────────┐
  │ TIMER  │  │ SUBSCRIBER       │
  │Afgelopen?│ │Nieuw bericht?    │
  └────┬───┘  └──────────┬───────┘
       │YES              │YES
       ▼                 ▼
  timer_callback()  subscription_callback()
  
  Elke 1000 ms    Bij elk inkomend bericht
  Lees sensor     Verwerk Float32 waarde
  Publiceer Int16 Stuur actuator aan
```

### ROS 2 Bericht Flow

```
PUBLISHER FLOW (timer-gestuur):
  loop() → executor → timer_callback() 
         → publisher_information.data = sensor_reading
         → rcl_publish(&template_publisher, ...) 
         → Topic "/template_publisher" → Host PC

SUBSCRIBER FLOW (event-gestuur):
  Host PC → Topic "/template_subscriber" 
         → micro_ros_agent 
         → rcl_subscription 
         → subscription_callback()
         → subscriber_information = Float32_value
         → Actuator aansturen (jij!)
```

### Geheugenverdeling

| Component | Type | Voorzien |
|-----------|------|----------|
| Node | `rcl_node_t` | 1x |
| Publisher | `rcl_publisher_t` | 1x |
| Subscriber | `rcl_subscription_t` | 1x |
| Timer | `rcl_timer_t` | 1x |
| Executor | `rclc_executor_t` | 1x (max 2 handles) |
| Message buffer | `std_msgs__msg__*` | Auto-allocated |

---

## ROS 2 Commando's

### Topics Verkennen

```bash
# Alle topics zien
ros2 topic list

# Topic type en frequentie zien
ros2 topic info /template_publisher

# Echte berichten zien
ros2 topic echo /template_publisher
ros2 topic echo /template_subscriber --no-arr
```

### Berichten Versturen

```bash
# Eenmalig bericht versturen
ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 1.5}"

# Voortdurend bericht versturen (10 Hz)
ros2 topic pub -r 10 /template_subscriber std_msgs/msg/Float32 "{data: 2.71}"

# Voortdurend omlaag tellen
for i in {0..100..10}; do 
  ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: $i}"
  sleep 0.5
done
```

### Node Informatie

```bash
# Node zien
ros2 node list

# Node details (publishers, subscribers, services)
ros2 node info /microros_template_node
```

### ROS 2 Graph Visualiseren

```bash
# Interactieve visualizer (Linux/macOS)
rqt_graph
```

---

## Onderwerpen Gebruiken

### Topic: `/template_publisher`

- **Type**: `std_msgs/msg/Int16`
- **Frequentie**: 1 Hz (timer-trigger)
- **Inhoud**: Sensorwaarde (bijv. ADC reading, temperatuur, afstand)
- **Richting**: ESP32 → Host

**Testen:**

```bash
ros2 topic echo /template_publisher
# Output:
# data: 42
# ---
# data: 42
```

### Topic: `/template_subscriber`

- **Type**: `std_msgs/msg/Float32`
- **Trigger**: Event-driven (direct bij nieuw bericht)
- **Inhoud**: Commando (bijv. motorkracht, LED helderheid, servo hoek)
- **Richting**: Host → ESP32

**Testen:**

```bash
# Motor aansturen naar 75% vermogen
ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 0.75}"

# Servo naar 90 graden
ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 90}"

# Relais AAN (waarde > 0.5)
ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 1.0}"
```

---

## Aanpassingen voor Jouw Sensoren & Actuatoren

### 📖 Het Bestand Aanpassen

Open [`src/main.cpp`](src/main.cpp) en zoek de `TODO:`-commentaren.

### ✏️ TODO 1: Hardware Setup (setup-functie)

Voeg je eigen GPIO-initialisatie toe hier:

```cpp
void setup() {
  // TODO: STAP 2 - JE EIGEN HARDWARE SETUP
  
  // Analoge sensor (ADC)
  pinMode(A0, INPUT);
  analogSetAttenuation(ADC_11db);
  
  // Digitale sensor
  pinMode(SENSOR_PIN, INPUT);
  
  // Motor PWM
  ledcSetup(LED_CHANNEL, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcAttachPin(MOTOR_PIN, LED_CHANNEL);
}
```

### ✏️ TODO 2: Sensor Uitlezen (timer_callback)

Lees sensordata in plaats van dummywaarde:

```cpp
void timer_callback(rcl_timer_t * timer, int64_t last_call_time) {
  if (timer != NULL) {
    // TODO: STAP 1 - SENSORDATA INLEZEN
    
    // Analoge waarde lezen (0-4095 -> 0-100)
    int raw = analogRead(A0);
    publisher_information.data = raw / 40;
    
    // Of: digitale waarde
    if (digitalRead(SENSOR_PIN)) {
      publisher_information.data = 1;
    }
    
    RCSOFTCHECK(rcl_publish(&template_publisher, &publisher_information, NULL));
  }
}
```

### ✏️ TODO 3: Actuator Aansturen (subscription_callback)

Zet actuatoren aan op basis van Float32:

```cpp
void subscription_callback(const void * msgin) {
  const std_msgs__msg__Float32 * msg = (const std_msgs__msg__Float32 *)msgin;
  if (msg == NULL) return;
  
  subscriber_information.data = msg->data;
  
  // TODO: STAP 2 - HARDWARE-ACTUATOREN AANSTUREN
  
  // PWM naar motor (0.0-1.0 -> 0-255)
  int pwm_value = (int)(msg->data * 255.0);
  analogWrite(MOTOR_PIN, pwm_value);
  
  // Of: servo naar hoek (0.0-180.0)
  servo.write((int)(msg->data));
  
  // Of: relais AAN/UIT
  if (msg->data > 0.5) {
    digitalWrite(RELAY_PIN, HIGH);
  } else {
    digitalWrite(RELAY_PIN, LOW);
  }
  
  Serial.printf("Actuator set to: %.2f\n", msg->data);
}
```

---

## Voorbeelden: Sensor + Actuator Combinaties

### 📌 Voorbeeld 1: Temperatuur Sensor → Fan PWM

```cpp
// Hardware:
// - DHT22 temperatuursensor (GPIO 4)
// - PWM fan controller (GPIO 5)

// setup():
#include <DHT.h>
#define DHT_PIN 4
DHT dht(DHT_PIN, DHT22);
dht.begin();
ledcSetup(0, 1000, 8);  // 1 kHz, 8-bit resolution
ledcAttachPin(5, 0);

// timer_callback():
float temp = dht.readTemperature();
publisher_information.data = (int16_t)temp;

// subscription_callback():
int fan_speed = (int)(msg->data * 255);  // 0-255
ledcWrite(0, fan_speed);
```

### 📌 Voorbeeld 2: Ultrasonic Distance → Servo

```cpp
// Hardware:
// - Ultrasonic sensor HC-SR04 (TRIG=12, ECHO=13)
// - Servo (GPIO 14)

// timer_callback():
digitalWrite(12, LOW);
delayMicroseconds(2);
digitalWrite(12, HIGH);
delayMicroseconds(10);
digitalWrite(12, LOW);
long duration = pulseIn(13, HIGH);
int distance = (int)(duration * 0.034 / 2);
publisher_information.data = distance;

// subscription_callback():
servo.write((int)(msg->data));  // 0-180 degrees
```

### 📌 Voorbeeld 3: Light Sensor → LED Brightness

```cpp
// Hardware:
// - LDR (Light Dependent Resistor) op ADC1
// - RGB LED (GPIO 15, 16, 17 met PWM)

// timer_callback():
int light_level = analogRead(A1) / 16;  // 0-255
publisher_information.data = light_level;

// subscription_callback():
int brightness = (int)(msg->data * 255);
ledcWrite(0, brightness);  // Red channel
ledcWrite(1, brightness);  // Green channel
ledcWrite(2, brightness);  // Blue channel
```

---

## Troubleshooting

### ❌ Probleem: "micro-ROS Agent Connection Failed"

**Symptoom**: Seriële monitor toont geen "Setup voltooid"

**Oorzaken & Oplossingen**:

1. **Agent niet draaiend?**
   ```bash
   # Terminal op host: agent starten
   ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
   
   # Controleer ROS 2 setup
   printenv | grep ROS_
   ```

2. **Verkeerde USB-poort?**
   ```bash
   # Linux: controleer beschikbare poorten
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # macOS
   ls /dev/tty.usbserial* /dev/tty.SLAB_*
   ```

3. **Baudrate mismatch?**
   - `platformio.ini`: `monitor_speed = 115200`
   - Agent: `-b 115200`
   - Beide moeten match!

### ❌ Probleem: "Cannot Upload - Port Locked"

**Symptoom**: PlatformIO kan niet flashen

**Oorzaken & Oplossingen**:

```bash
# Kill andere processen op USB-poort
sudo fuser -k /dev/ttyUSB0

# Of: seriële monitor sluiten in VS Code
# VS Code → PlatformIO → Serial Monitor → Stop
```

### ❌ Probleem: "Topic List Empty"

**Symptoom**: `ros2 topic list` toont geen topics

**Oorzaken & Oplossingen**:

```bash
# 1. Controleer ROS setup
source /opt/ros/<distro>/setup.bash

# 2. Controleer agent verbinding
# Seriële monitor: "Setup voltooid" zien?

# 3. Wacht even - topics kunnen 2-3 sec duren om registreren
sleep 3
ros2 topic list
```

### ❌ Probleem: "USB Device Not Recognized"

**Windows Symptoom**: COM poort niet zichtbaar

**Oplossing**:

1. CH340/CH341 driver installeren:
   - Download: https://github.com/WCHSoftware/ch341ser
   
2. USB kabel proberen met ander poort
   
3. ESP32 board opnieuw uploaden:
   ```bash
   platformio run --target erase
   platformio run --target upload
   ```

### ✅ Foutopsporing: Seriële Monitor Gebruiken

```bash
# Verbinding testen
platformio device monitor -b 115200

# Probeer te typen - zie je echo?
# Zeker weten dat agent verbinding heeft?
```

Controleer seriële output:
```
[Timer] Publishing: 42 at 1000ms interval
[Subscriber] Received: 3.14
[DEBUG] System running normally
```

---

## Project Structuur

```
microros_template/
├── platformio.ini          # PlatformIO configuratie (board, port, libraries)
├── README.md              # Dit bestand!
│
├── src/
│   └── main.cpp           # Hoofd-applicatielogica
│                           #   - timer_callback() — Publisher
│                           #   - subscription_callback() — Subscriber
│                           #   - setup() — ROS 2 init
│                           #   - loop() — Event-gestuurd
│
├── include/
│   └── README             # Plek voor custom headers
│
├── lib/
│   └── README             # Plek voor custom C++ libraries
│
└── test/
    └── README             # Plek voor unit tests
```

---

## Next Steps

### Fase 1: Verkenning ✅ (jij bent hier)

- [x] Compileren en flashen
- [x] Seriële monitor controleren
- [x] Micro-ROS agent verbonden
- [x] Publisher/Subscriber werkend

### Fase 2: Sensoren Toevoegen

- [ ] Sensor GPIO pinnen definiëren
- [ ] `timer_callback()` aanpassen voor sensor uitlezen
- [ ] Publisher test middel `ros2 topic echo`

### Fase 3: Actuatoren Toevoegen

- [ ] Actuator GPIO pinnen definiëren
- [ ] `subscription_callback()` aanpassen voor actuator control
- [ ] Testen met `ros2 topic pub`

### Fase 4: Integratie

- [ ] ROS 2 launch-files aanmaken
- [ ] Parameter server gebruiken
- [ ] Services toevoegen (optioneel)

---

## Referenties

### Officiële Documentatie

- 📚 [Micro-ROS Documentation](https://micro.ros.org/)
- 📚 [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- 📚 [PlatformIO Documentation](https://docs.platformio.org/)
- 📚 [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)

### Handige Links

- 🔗 Micro-ROS Platform Support: https://micro.ros.org/docs/ecosystem/rtos/
- 🔗 ROS 2 Topic Cheat Sheet: https://docs.ros.org/en/humble/Tutorials/Topics/Understanding-ROS2-Topics.html
- 🔗 ESP32 Pinout Diagrams: https://randomnerdtutorials.com/esp32-pinout-reference-gpios/

---



**Veel succes met je micro-ROS project! 🚀**
