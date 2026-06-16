/*
 * ============================================================================
 * MICRO-ROS TEMPLATE VOOR ESP32
 * ============================================================================
 * Dit programma implementeert een eenvoudige micro-ROS node met:
 *   - Een PUBLISHER die periodiek sensorsignalen verstuurt
 *   - Een SUBSCRIBER die berichten van ROS 2 ontvangt
 *   - Een TIMER die beide callbacks periodiek triggert
 *   - Foutafhandeling met statusled
 *
 * Vereisten:
 *   - ESP32 Dev board (WROOM of C3 variant)
 *   - micro-ROS agent draaien op host:
 *     ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
 * ============================================================================
 */

#include <Arduino.h>
#include <micro_ros_platformio.h>

// ROS 2 C API headers voor node, publisher, subscriber en executor 
#ifdef __cplusplus
extern "C" {
#endif
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#ifdef __cplusplus
}
#endif

// Bericht-types: Int16 voor publisher, Float32 voor subscriber
#include <std_msgs/msg/int16.h>
#include <std_msgs/msg/float32.h>


// Compilatie-check: deze template werkt ALLEEN via seriële transport
#if !defined(MICRO_ROS_TRANSPORT_ARDUINO_SERIAL)
#error This template is only avaliable for Arduino framework with serial transport.
#endif


// ============================================================================
// GLOBALE ROS 2 OBJECTEN
// ============================================================================

// PUBLISHER: verzend bericht naar topic "template_publisher"
//   - Berichten van type std_msgs/msg/Int16
//   - Inhoud wordt ingesteld in timer_callback()
rcl_publisher_t template_publisher;
std_msgs__msg__Int16 publisher_information;

// SUBSCRIBER: luister naar topic "template_subscriber"
//   - Berichten van type std_msgs/msg/Float32
//   - Nieuwe berichten activeren subscription_callback()
rcl_subscription_t template_subscription;
std_msgs__msg__Float32 subscriber_information;

// EXECUTOR: centrale "eventlus" die timers en subscribers verwerkt
//   - In loop() wordt executor_spin_some() aangeroepen
//   - Dit voert alle pending callbacks uit
rclc_executor_t executor;

// SUPPORT: bevat context en initialiseringsdata voor de ROS-middleware
//   - Init eenmalig in setup()
//   - Gebruikt door node, publisher, subscriber, etc.
rclc_support_t support;

// ALLOCATOR: defines hoe geheugen wordt beheerd (malloc/free)
//   - Standaard allocator : gewoon standard libc malloc/free
rcl_allocator_t allocator;

// NODE: representatie van deze ESP32 als ROS 2 node
//   - Zichtbaar in ROS 2 via `ros2 node list`
//   - Naam vastgesteld in NODE_NAME macro
rcl_node_t node;

// TIMER: triggert timer_callback() met vaste interval (1000 ms = 1 Hz)
//   - Periodiek publiceren van sensordata
rcl_timer_t timer;

// ============================================================================
// CONFIGURATIE EN MACROS
// ============================================================================

// Node-naam: zichtbaar in `ros2 node list` en `ros2 topic list`
#define NODE_NAME "microros_template_node"

// RCCHECK: HARDE FOUTCONTROLE - stopt alles op kritische fouten
// Gebruikt voor installatie van publisher, subscriber, executor
// Bij fout: activeer error_loop() die LED knippert en systeem herstart
//
// Voorbeeld:
//   RCCHECK(rclc_node_init_default(&node, NODE_NAME, "", &support));
//   Als initialisatie faalt: krimp LED en ESP.restart()
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}

// RCSOFTCHECK: ZACHTE FOUTCONTROLE - errors worden genegeerd
// Gebruikt voor operaties die mogen falen zonder systeem stop
// Voorbeeld: publiceren van bericht mis gaat? Ga gewoon door naar volgende cycle
//
// Voorbeeld:
//   RCSOFTCHECK(rcl_publish(&template_publisher, &publisher_information, NULL));
//   Als publiceren faalt: niets gebeurt (geen error_loop)
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

// ============================================================================
// GLOBALE VARIABELEN EN FOUTAFHANDELING
// ============================================================================

// État van de status-LED tijdens foutknipperen (true = HIGH, false = LOW)
bool errorLedState = false;


// FOUTAFHANDELING: error_loop()
// ============================================================================
// Deze functie wordt aangeroepen wanneer een RCCHECK() macro een fout detecteert.
// 
// Gedrag:
//   1. Print foutmelding naar seriële console
//   2. Knippert STATUS_LED_PIN 20x als visuele waarschuwing
//   3. Roept ESP.restart() aan na timeout
//
// Dit is een "veilige toestand" - normaal programmaflow stopt hier.
// 
// Waarschijnlijke oorzaken van fout:
//   - Micro-ROS agent niet draaiend op host PC
//   - USB/seriële verbinding verbroken
//   - Onvoldoende geheugen op ESP32
//   - Onverwachte ROS-initialisatiefout
void error_loop(){
  int count = 0;
  
  // Log fout naar seriële monitor
  Serial.printf("Ultrasonic Sensor\nError\nSystem halted");
  
  // Knipperloop: LED aan/uit om visueel aan te geven dat iets mis is
  while(count < 20){
    if(errorLedState){
        // LED AAN
        digitalWrite(STATUS_LED_PIN, HIGH);
        errorLedState = false;
    }
    else{
        // LED UIT
        digitalWrite(STATUS_LED_PIN, LOW);
        errorLedState = true;
    }
    // 100 ms wachten tussen staatwisseling (2 sec totale knippersequentie)
    delay(100);
    count++;
  }
  
  // Herstart ESP32 na foutknippersequentie
  ESP.restart();
}

// ============================================================================
// TIMER-CALLBACK: Periodiek publiceren van sensordata
// ============================================================================
// Deze functie wordt elke 1000 ms (1 Hz) aangeroepen door de executor.
// 
// Stappen:
//   1. Last_call_time parameter ongebruikt - RCLC_UNUSED markeren
//   2. Controleer of timer pointer geldig is
//   3. Lees sensordata en sla op in publisher_information.data
//   4. Publiceer bericht op topic "template_publisher"
//
// Parameters:
//   timer: pointer naar de ROS timer (gecontroleerd in if-statement)
//   last_call_time: timestamp van vorige callback call (niet gebruikt)
void timer_callback(rcl_timer_t * timer, int64_t last_call_time) {
  // Zeg tegen compiler dat last_call_time bewust niet gebruikt wordt
  RCLC_UNUSED(last_call_time);
  
  // Veiligheidschecks
  if (timer != NULL) {
    // ========================================================================
    // TODO: STAP 1 - SENSORDATA INLEZEN
    // ========================================================================
    // Vervang deze dummywaarde door actualere sensorwaardes:
    //
    //   analogValue = analogRead(A0);          // ADC van analoge sensor
    //   publisher_information.data = analogValue / 16;  // Schaal naar Int16
    //
    //   of voor digitale sensoren:
    //   if (digitalRead(SENSOR_PIN)) {
    //     publisher_information.data = 1;
    //   } else {
    //     publisher_information.data = 0;
    //   }
    //
    publisher_information.data = 42;  // Dummywaarde (vervang door echte sensor!)

    // ========================================================================
    // STAP 2 - BERICHT PUBLICEREN
    // ========================================================================
    // Verstuur publisher_information naar ROS 2 topic "template_publisher"
    // RCSOFTCHECK: als publiceren faalt, gaat loop gewoon door
    // Dit voorkomt dat 1 gefaalde publish het hele systeem stopt
    RCSOFTCHECK(rcl_publish(&template_publisher, &publisher_information, NULL));
    
    // Optioneel: log naar seriële monitor (alleen voor debugging)
    // Serial.printf("Published Int16: %d\n", publisher_information.data);
  }
}

// ============================================================================
// SUBSCRIBER-CALLBACK: Ontvangen van ROS 2-berichten
// ============================================================================
// Deze functie wordt aangeroepen ZODRA een nieuw bericht binnenkomt op
// topic "template_subscriber" (type: std_msgs/msg/Float32).
//
// Stappen:
//   1. Cast de void pointer naar Float32 pointer
//   2. Controleer op NULL pointer (foute bericht)
//   3. Verwerk het ontvangen bericht (bijv. motor sturen, LED dimmen)
//
// Voorbeeld berichten verzenden vanuit ROS 2 PC:
//   ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 3.14}"
//
// Parameters:
//   msgin: void pointer naar Float32 bericht (moet gecast worden)
void subscription_callback(const void * msgin) {
  // Cast van void* naar Float32* (type-safe bericht)
  const std_msgs__msg__Float32 * msg = (const std_msgs__msg__Float32 *)msgin;
  
  // Veiligheidschecks: controleer NULL pointer
  if (msg == NULL) {
    Serial.println("ERROR: NULL message in subscription_callback");
    return;
  }
  
  // ========================================================================
  // TODO: STAP 1 - ONTVANGEN DATA VERWERKEN
  // ========================================================================
  // Sla ontvangen Float32 waarde op voor gebruik in loop()
  subscriber_information.data = msg->data;
  
  // Debug output naar seriële monitor
  Serial.printf("[SUBSCRIBER] Ontvangen Float32: %.2f\n", msg->data);
  
  // ========================================================================
  // TODO: STAP 2 - HARDWARE-ACTUATOREN AANSTUREN (optional)
  // ========================================================================
  // Voorbeelden:
  //
  //   1. PWM-signaal naar motor variëren:
  //      int pwm_value = (int)(msg->data * 255.0);  // 0.0-1.0 naar 0-255
  //      analogWrite(MOTOR_PIN, pwm_value);
  //
  //   2. LED dimmen met PWM:
  //      ledcWrite(LED_CHANNEL, (int)(msg->data * 256));
  //
  //   3. Relais AAN/UIT op basis van drempel:
  //      if (msg->data > 0.5) {
  //        digitalWrite(RELAY_PIN, HIGH);
  //      } else {
  //        digitalWrite(RELAY_PIN, LOW);
  //      }
  //
  //   4. Servo naar hoek (0-180 graden):
  //      servo.write((int)(msg->data));
  //
}

// ============================================================================
// SETUP: Eenmalige initialisatie van hardware en ROS 2
// ============================================================================
// Deze functie wordt EENMALIG uitgevoerd na opstarten van de ESP32.
void setup() {
  // ========================================================================
  // STAP 1: HARDWARE-PINNEN INITIALISEREN
  // ========================================================================
  
  // Status-LED: visuele feedback gedurende opstart en bij fouten
  pinMode(STATUS_LED_PIN, OUTPUT); 
  digitalWrite(STATUS_LED_PIN, HIGH);  // LED AAN als indicatie opstart

  // ========================================================================
  // TODO: STAP 2 - JE EIGEN HARDWARE SETUP
  // ========================================================================
  // Voeg hier initialisatie toe voor je sensoren en actuatoren:
  //
  //   // Analoge sensor (ADC)
  //   pinMode(A0, INPUT);
  //   analogSetAttenuation(ADC_11db);
  //
  //   // Digitale sensor
  //   pinMode(SENSOR_PIN, INPUT);
  //
  //   // Motor PWM
  //   ledcSetup(LED_CHANNEL, PWM_FREQUENCY, PWM_RESOLUTION);
  //   ledcAttachPin(MOTOR_PIN, LED_CHANNEL);
  //
  //   // Servo
  //   servo.attach(SERVO_PIN);
  //   servo.write(90);
  //

  // ========================================================================
  // STAP 3: SERIËLE COMMUNICATIE STARTEN
  // ========================================================================
  // Seriële poort voor debug-output en micro-ROS transport
  // Baudrate 115200: standaard voor ESP32 en micro-ROS agent
  Serial.begin(115200);
  
  Serial.println("\n\n===============================================");
  Serial.println("MICRO-ROS TEMPLATE OPSTARTEN");
  Serial.println("===============================================\n");

  // ========================================================================
  // STAP 4: MICRO-ROS TRANSPORT CONFIGUREREN
  // ========================================================================
  // Stel seriële verbinding in als transport-medium naar micro-ROS agent
  // De agent op je PC communiceert via deze seriële lijn
  set_microros_serial_transports(Serial);

  // Wachttijd voor seriële stabilisering en agent-verbinding
  // Geeft de micro-ROS agent tijd om verbinding tot stand te brengen
  Serial.println("Wachten op micro-ROS agent verbinding (2 sec)...");
  delay(2000);

  // ========================================================================
  // STAP 5: ROS 2 MIDDLEWARE INITIALISEREN
  // ========================================================================
  
  // 5a. Allocator: geeft aan hoe geheugen in ROS mag worden beheerd
  // rcl_get_default_allocator() gebruikt standard libc malloc/free
  Serial.println("Initialiseer geheugen-allocator...");
  allocator = rcl_get_default_allocator();

  // 5b. Support-struct: basis-infrastructure voor ROS context
  // Dit moet VOOR alle andere ROS-initialisaties gebeuren
  // Error: stopt systeem met error_loop() als dit faalt
  Serial.println("Initialiseer ROS 2 support context...");
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));

  // 5c. Node: representatie van deze ESP32 als ROS 2 node
  // Naam: NODE_NAME ("microros_template_node")
  // Dit maakt de node zichtbaar in `ros2 node list` op de host
  Serial.printf("Maak ROS 2 node aan: %s\n", NODE_NAME);
  RCCHECK(rclc_node_init_default(&node, NODE_NAME, "", &support));


  // ========================================================================
  // STAP 6: PUBLISHER INITIALISEREN
  // ========================================================================
  // Publisher voor periodiek versturen van sensordata
  //
  // Topic-naam:    "template_publisher"
  // Bericht-type:  std_msgs/msg/Int16
  // Frequentie:    1 Hz (ingesteld in timer)
  //
  // Testen: ros2 topic echo /template_publisher
  Serial.println("Initialiseer publisher (topic: template_publisher)...");
  RCCHECK(rclc_publisher_init_default(
    &template_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int16),
    "template_publisher"));

  // ========================================================================
  // STAP 7: SUBSCRIBER INITIALISEREN
  // ========================================================================
  // Subscriber voor ontvangen van ROS 2-commando's
  //
  // Topic-naam:    "template_subscriber"
  // Bericht-type:  std_msgs/msg/Float32
  // Trigger:       ON_NEW_DATA (callback bij elk nieuw bericht)
  //
  // Testen: ros2 topic pub /template_subscriber std_msgs/msg/Float32 "{data: 3.14}"
  Serial.println("Initialiseer subscriber (topic: template_subscriber)...");
  RCCHECK(rclc_subscription_init_default(
    &template_subscription,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32),
    "template_subscriber"));


  // ========================================================================
  // STAP 8: PERIODIEKE TIMER CONFIGUREREN
  // ========================================================================
  // Timer: activeert timer_callback() elke N milliseconden
  //
  // Timeout: 1000 ms = 1 Hz (sensor lezen + publiceren 1x per seconde)
  // Aanpassen: 500 ms = 2 Hz, 2000 ms = 0.5 Hz, etc.
  //
  // RCL_MS_TO_NS: converteert milliseconden naar nanoseconden
  // (ROS 2 werkt intern met nanoseconden precisie)
  const unsigned int timer_timeout = 1000;  // milliseconden
  
  Serial.printf("Initialiseer timer (%u ms = %.1f Hz)...\n", timer_timeout, 1000.0/timer_timeout);
  RCCHECK(rclc_timer_init_default(
    &timer,
    &support,
    RCL_MS_TO_NS(timer_timeout),  // RCL_MS_TO_NS: 1000 ms = 1000000000 ns
    timer_callback));

  // ========================================================================
  // STAP 9: EXECUTOR INITIALISEREN EN CALLBACKS REGISTREREN
  // ========================================================================
  // Executor: centrale "event dispatcher" die alle callbacks verwerkt
  //
  // Initialisatie:
  //   - support.context: ROS context (eerder aangemaakt)
  //   - 2: aantal "handles" die executor kan verwerken (1 timer + 1 subscriber)
  //   - allocator: geheugen-manager
  //
  Serial.println("Initialiseer executor met 2 handles (timer + subscriber)...");
  RCCHECK(rclc_executor_init(&executor, &support.context, 2, &allocator));
  
  // Voeg timer toe aan executor
  // Elke 1000 ms zal executor timer_callback() aanroepen
  Serial.println("  -> Voeg timer toe aan executor");
  RCCHECK(rclc_executor_add_timer(&executor, &timer));
  
  // Voeg subscriber toe aan executor
  // Bij elk nieuw bericht op topic "template_subscriber" wordt subscription_callback() aanroepen
  // ON_NEW_DATA: callback ook direct uitvoeren (niet wachten op timer)
  Serial.println("  -> Voeg subscriber toe aan executor");
  RCCHECK(rclc_executor_add_subscription(
    &executor,
    &template_subscription,
    &subscriber_information,
    &subscription_callback,
    ON_NEW_DATA));  // Trigger: bij ELKE nieuwe Float32

  // ========================================================================
  // STAP 10: OPSTARTSEQUENTIE AFGEROND
  // ========================================================================
  // Zet LED uit als aanduiding dat setup() voltooid is
  // Systeem staat nu in "normaal bedrijf" - ready voor inkomende berichten
  digitalWrite(STATUS_LED_PIN, LOW);
  
  Serial.println("\n✓ Setup voltooid! Systeem draait normaal.");
  Serial.println("  Node naam:     microros_template_node");
  Serial.println("  Publisher:     /template_publisher (Int16)");
  Serial.println("  Subscriber:    /template_subscriber (Float32)");
  Serial.println("  Timer:         1000 ms (1 Hz)");
  Serial.println("\nWachtend op ROS 2-berichten via micro-ROS agent...");
  Serial.println("===============================================\n");
}

// ============================================================================
// SETUP() EINDE
// ============================================================================

// ============================================================================
// LOOP: Centrale eventlus (draait oneindig)
// ============================================================================
// Deze functie wordt oneindig herhaald door Arduino framework.
// Hier laten we de executor zijn werk doen:
//   - Timer aflopen? -> timer_callback() activeren
//   - Nieuw subscriber-bericht? -> subscription_callback() activeren
//
// De loop draait op CPU-core 1 (core 0 = WiFi/BLE stack)
//
void loop() {
  // ========================================================================
  // Vertraging: voorkomen van spinloop die CPU 100% belast
  // ========================================================================
  // 100 ms wachten tussen executor-cycles
  // Dit geeft de CPU tijd voor ander werk (WiFi, BLE, etc.)
  delay(100);
  
  // ========================================================================
  // EXECUTOR SPIN: verwerk pending callbacks
  // ========================================================================
  // rclc_executor_spin_some():
  //   - Controleer alle geregistreerde timers/subscribers op events
  //   - Als timer afgelopen: roep timer_callback() aan
  //   - Als subscriber-bericht aangekomen: roep subscription_callback() aan
  //   - Timeout: 100 ms wachten op events
  //
  // RCSOFTCHECK: zachte foutafhandeling
  //   Executor faalt? Log fout maar ga door met volgende cycle
  //
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
  
  // ========================================================================
  // OPTIONEEL: Eigen applicatielogica in loop
  // ========================================================================
  // Hier kan je code toevoegen die ÓNAFHANKELIJk van callbacks draait:
  //
  //   // Bv: iedere 5 seconden iets doen (zonder timer):
  //   static unsigned long last_action = 0;
  //   if (millis() - last_action > 5000) {
  //     Serial.println("5 seconden verstreken");
  //     last_action = millis();
  //   }
  //
  //   // Bv: hardware-status monitoren:
  //   battery_voltage = analogRead(BATT_PIN);
  //   temperature = readTemperatureSensor();
  //
}