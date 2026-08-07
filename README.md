IOT-based Washroom Odor Detection system


	Overview:
 This project is the Real-Time IoT-based Washroom Odor Detection System designed using the Raspberry Pi Pico 2 W using MicroPython. This system detects the washroom environment by analyzing the values of temperature, humidity, and Ammonia (NH3), and Hydrogen Sulfide (H2S) levels with the help of sensors. The data captured is then translated to JSON and sent to a secure web server using Wi-Fi.
 The system gives visual feedback on its status by using LEDs according to the calculated Washroom Health Index (WHI), drives local LED status indicators, and uploads structured JSON records to a cloud API over HTTPS.

	Features:

I.	Temperature and Humidity Sensor in Real Time
II.	Air Quality Sensor using MQ135 Gas Sensor
III.	Temperature & Humidity sensor using DHT22 Sensor
IV.	Synchronize the system time using an NTP Server
V.	Wi-Fi Connection
VI.	Automatic JSON Data Upload on Secure Server
VII.	Washroom Health Status Display using LED Lights
VIII.	Automatic Memory Management Using Garbage Collection
IX.	Support for RTC Module
X.	Non-blocking Delay Function
XI.	API Key Authentication for Data Upload on Secure Server
XII.	To indicate washroom status the LED indicator (Green/Red).



	Hardware Used:
I.	Raspberry Pi Pico 2W-
a.	The Raspberry Pi Pico 2 W is the main controller of the system.
b.	It is based on the RP2350 microcontroller with in-build  Wi-Fi.
c.	It supports Micropython and C/C++ programming.
d.	It continuously reads sensor values through GPIO and ADC pins.
e.	The controller processes the data, creates a JSON object and transmits it over Wi-Fi or Ethernet.
f.	It acts as the central processing unit of the IoT monitoring system.

II.	DHT22 Temperature & Humidity Sensor-
a.	The DHT22 is a digital temperature and humidity sensor.
b.	It measures humidity from 0% to 100% RH.
c.	It communicates with Pico using a single digital data pin.
d.	The sensor uses a capacitive humidity sensing element and a thermistor. It converts the measurements into digital data and sends them to the microcontroller.
e.	The measured values are used to evaluate the washroom environment.

III.	MQ135 Gas Sensor-
a.	The MQ135 detects harmful gases(NH3,CO2,smoke) and poor air quality.
b.	It operates using 5V power supply and provides an analog voltage output.
c.	It is connected to an ADC pin of the Pico.
d.	The sensing material changes its resistances when exposed to gases the output voltage changes according to gas concentration Pico converts it into digital values.


IV.	18650 3.7V 2000mAh Lithium-Ion Battery-
a.	The 18650 battery provides portable power to the system.It is a rechargeable lithium-ion battery.
b.	It has a nominal voltage of 3.7 V.It offers a capacity of approximately 2000 mAh.
c.	The battery stores electrical energy through reversible chemical reactions. During operation, it supplies DC power to the circuit until recharging is required.

V.	USB Power Supply-
a.	The USB power supply provides stable DC power to the system.
b.	It typically supplies 5 V output.
c.	It powers the Raspberry Pi Pico and connected modules.
d.	The USB source converts AC mains power into regulated 5 V DC. The regulated voltage is delivered to the controller and peripherals.

VI.	W5500 Ethernet Cable-
a.	The W5500 is a hardware TCP/IP Ethernet controller. It provides wired network connectivity.
b.	It communicates with the Pico through the SPI interface.
c.	It reduces the processing load on the microcontroller.
d.	The Pico sends network data to the W5500 via SPI. The W5500 converts the data into Ethernet packets. The packets are transmitted to the server through the Ethernet cable.


VII.	Charger Module (7.8V 2S Charging Module)-
a.	The charging module safely charges rechargeable batteries.
b.	The module monitors battery voltage throughout the charging process.
c.	It automatically reduces or stops charging when the battery reaches full capacity.

VIII.	Green LED and Red LED –
a.	The green LED indicates a healthy washroom condition and The red LED indicates poor environmental conditions.
b.	It is connected to a GPIO pin.
c.	Current flows through the LED when the GPIO pin is driven LOW.
d.	The LED emits green light to indicate acceptable air quality and The LED glows red whenever the air quality exceeds the defined threshold.

IX.	Zero PCB-
a.	The Zero PCB is used for mounting and interconnecting all electronic components of the prototype.
b.	It provides a compact and organized platform for soldering the sensors, communication modules, LEDs, and power supply circuitry, resulting in a robust hardware assembly.
X.	PCB-
a.	The protective enclosure is fabricated using Acrylonitrile Butadiene Styrene (ABS), a durable and lightweight engineering thermoplastic.
b.	It is designed to securely house the Raspberry Pi Pico 2W, MQ-135 sensor, PCB, and other electronic components while protecting them from dust, moisture, and accidental 
damage.


















	Software Requirement:
I.	MicroPython-
a.	MicroPython is a lightweight version of Python designed for microcontrollers.
b.	It is used to program the Raspberry Pi Pico 2 W.
c.	It provides simple syntax for controlling hardware peripherals.
d.	Library-
i.machine- Controls GPIO pins and hardware peripherals  such as SPI, ADC, and digital I/O.
ii.	Network- Establishes network connectivity through Wi-Fi or Ethernet.
iii.	Urequests- Sends HTTP requests to transmit sensor data to the API.
iv.	Dht -Reads temperature and humidity data from the DHT22 sensor.
v.	Time- Provides timing and delay functions for periodic sensor acquisition.
vi.	Json - Encodes and decodes data in JSON format for communication with the API.
vii.	Ntptime- Synchronizes the Raspberry Pi Pico 2 W with an NTP server to obtain accurate date and time for timestamping sensor data.
viii.	Gc-Performs automatic memory management by reclaiming unused memory, helping maintain stable system performance during continuous operation.

II.	Thonny IDE-
a.	Thonny IDE is a beginner-friendly integrated development environment for Python and MicroPython.
b.	It supports direct file management on MicroPython devices.
c.	It provides an integrated serial terminal for debugging.

III.	JSON (JavaScript Object Notation)-
a.	JSON is a lightweight format for storing and exchanging data.
b.	It organizes sensor readings into a structured format.


IV.	HTTP REST API-
a.	A REST API enables communication between the IoT device and the web server.
b.	The Raspberry Pi Pico sends sensor data using HTTP POST requests.

V.	WiFi Networking-
a.	Wi-Fi networking provides wireless internet connectivity for the device.
b.	It connects the Raspberry Pi Pico 2 W to the local network.
c.	It allows real-time transmission of sensor data.

	System Architecture:

1.	The DHT22 sensor measures the temperature and humidity of the washroom environment.
2.	The MQ135 sensor detects air quality by sensing harmful gases and odor levels.
3.	The Raspberry Pi Pico 2 W collects data from all connected sensors.
4.	The Pico processes the sensor readings and converts them into a structured JSON format.
5.	The device connects to the network using Wi-Fi or an Ethernet module.
6.	The JSON data is securely transmitted to the remote server through an HTTP REST API.
7.	The server receives, validates, and stores the sensor data in a database.
8.	The web application retrieves the stored data and displays real-time sensor values and system status.
9.	The Green and Red LEDs provide local visual indication of the washroom health condition.
10.	The entire process repeats continuously, enabling real-time environmental monitoring and remote access to the sensor data.















DHT22 Sensor ──┐
│
MQ135 Sensor ──┼──> Raspberry Pi Pico 2 W
│
Green/Red LEDs
│
▼
JSON Data Generation
│
▼
Wi-Fi / Ethernet Module
│
▼
HTTP REST API (Server)
│
▼
Database / Cloud Storage
│
▼
Web Dashboard (Real-Time Monitoring)

	Pin Configuration
Component	Raspberry Pi Pico 2 W Pin	Configuration
DHT22 Temperature & Humidity Sensor	GPIO 15	Digital Input
MQ135 Gas Sensor	GPIO 26 (ADC0)	Analog Input (ADC)
Green LED	GPIO 16	Digital Output (Active-Low)
Red LED	GPIO 17	Digital Output (Active-Low)
Onboard Wi-Fi LED	Built-in LED	Digital Output
W5500 Ethernet Module	SPI Interface (if used)	SPI Communication
		

	Project Structure-

Project/
│
├── main.py
├── sensor_data.json
├── README.md

	Configuration:

WIFI_SSID
WIFI_PASSWORD
SERVER_URL
API_KEY
deviceId

Example:

WIFI_SSID = "Your_WiFi_Name"
WIFI_PASSWORD = "Your_Password"
SERVER_URL = "https://yourserver.com/api/upload-json"
API_KEY = "Your_API_Key"
deviceId = "Intern-pico-01"

	Circuit Design-
                                      The initial circuit of the proposed system was developed on a breadboard to verify the functionality and interconnection of the primary hardware components. The Raspberry Pi Pico 2 W serves as the central controller and is interfaced with the MQ-135 gas sensor for air quality monitoring and the DHT22 sensor for measuring temperature and humidity. The W5500 TCP Ethernet Module is connected to the Raspberry Pi Pico 2 W through the SPI communication interface, enabling network communication for transmitting sensor data to the centralized API. This breadboard implementation was used to validate the sensor readings, communication interface, and overall system operation before the hardware was assembled on the Zero PCB and integrated into the final prototype.


PCB Diagram-
                                     After successful breadboard testing, the system was assembled on a Zero PCB to create the final hardware prototype. The PCB integrates the Raspberry Pi Pico 2 W, MQ-135 sensor, DHT22 sensor, W5500 Ethernet module, LEDs, battery backup circuit, and supporting components. Proper component placement and soldering ensure reliable connections, compact design, and stable system operation.

Enclosure Design
A custom enclosure was designed in TinkerCAD and fabricated using 3D-printed ABS material to house all the system components. It provides a compact, durable, and protective structure with ventilation for accurate sensor measurements and dedicated openings for the Ethernet cable, USB Type-C port, and LED indicators. The enclosure protects the electronics from dust and physical damage, making the system suitable for airport washroom installation.

	WHI (Washroom Health Index) Calculation:

WHI Formula:

WHI = 100 - (P_{NH3} + P_{Temp} + P_{Humidity}+ P_{H2S})

Where:
•	WHI = Washroom Health Index (0–100)
•	P_NH3 = NH3 penalty
•	P_Temp = Temperature penalty
•	P_Humidity = Humidity penalty
•	P_H2S = H2S penalty

WHI Classification
WHI Range	Status	LED Indication
80–100	Good Environment	Green LED ON
50–79	Moderate Condition	Warning
0–49	Poor Condition	Red LED ON

	JSON Data Format:


  

	Application:
•	 Airport washroom monitoring systems.
•	Real-time IoT-based air quality monitoring.
•	Schools,Colleges,Shopping malls and commercial buildings.
•	Industrial sanitation monitoring.

	Future Improvement:
•	Integrate additional gas sensors (CO2) such as H₂S and NH₃ for improved odor detection.
•	Add SMS and email notification features.
•	Include GPS for location-based monitoring.
•	Add an OLED/LCD display for local data visualization.
•	Implement AI/ML algorithms for odor prediction and anomaly detection.
•	Support cloud platforms such as AWS, Azure, or Google Cloud.

	Troubleshooting:
•	  Verify that the Wi-Fi SSID and password are correct if the device cannot connect.
•	Ensure the server URL and API key are properly configured.
•	Check all sensor wiring and GPIO connections.
•	Confirm that the DHT22 and MQ135 sensors are functioning correctly.
•	Verify that the Raspberry Pi Pico 2 W is receiving a stable power supply.
•	Check the internet connection if data is not uploaded to the server.
•	Inspect LED indicators to identify the current system status.
•	Restart the device after making configuration changes.
•	 Review serial monitor output in Thonny IDE to identify runtime errors.
•	Update the MicroPython firmware and required libraries if compatibility issues occur.
























 















