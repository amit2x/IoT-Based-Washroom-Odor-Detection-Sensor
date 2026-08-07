from machine import Pin, ADC, RTC
import dht
import time
import json
import network
import urequests
import ntptime
import gc

# Enable automatic garbage collection
gc.enable()

# =====================================================
# WiFi + Server Config
# =====================================================
WIFI_SSID     = "Enter SSID"
WIFI_PASSWORD = "Password"
SERVER_URL    = "API End Point"
API_KEY       = "Enter Your API Key"

deviceId      = "Intern-pico-01"

# =====================================================
# HARDWARE CONFIGURATION
# =====================================================
wifi_led = Pin("LED", Pin.OUT)
wifi_led.off()

# WHI Indicator LEDs (Active-LOW Configuration)
# Anodes connected to 3.3V, Cathodes connected to GPIOs
green_led = Pin(16, Pin.OUT)
red_led   = Pin(17, Pin.OUT)

# In Active-LOW: High (1 / .on()) = LED OFF, Low (0 / .off()) = LED ON
green_led.on()  # Turn Green LED OFF initially
red_led.on()    # Turn Red LED OFF initially

JSON_FILE  = "sensor_data.json"
dht_sensor = dht.DHT22(Pin(15))
mq135      = ADC(26)

ADC_VREF = 3.3   # Pico ADC operates at 3.3V reference
VCC_MQ   = 5.0   # Sensor supply voltage for Rs calculation
RL       = 10.0  # Load resistance in kOhm
R0       = 230.0  # Calibrated sensor resistance in fresh air

print("v2.9 - Active-LOW (Sinking) LED Logic Applied")

# =====================================================
# Non-Blocking Delay Helper
# =====================================================
def non_blocking_delay(seconds):
    """
    Delays execution without freezing processor background loops.
    """
    start_ticks = time.ticks_ms()
    target_ms = int(seconds * 1000)
    
    while time.ticks_diff(time.ticks_ms(), start_ticks) < target_ms:
        time.sleep_ms(100)

# =====================================================
# WHI LED Control Helper (Active-LOW / Sinking Logic)
# =====================================================
def update_whi_leds(whi_value):
    if whi_value > 50:
        green_led.off()  # Pulls Pin 16 LOW -> Green LED turns ON
        red_led.on()     # Sets Pin 17 HIGH  -> Red LED turns OFF
        print("WHI Status: GOOD (>50) -> Green LED ON")
    else:
        green_led.on()   # Sets Pin 16 HIGH  -> Green LED turns OFF
        red_led.off()    # Pulls Pin 17 LOW -> Red LED turns ON
        print("WHI Status: POOR (<=50) -> Red LED ON")

# =====================================================
# Connect to WiFi & Sync Hardware Clock
# =====================================================
def connect_wifi(retries=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Disable Wi-Fi power saving mode (Performance Mode)
    try:
        wlan.config(pm=0xa11140)
    except Exception as e:
        print("Wi-Fi PM setting warning:", e)
    
    if wlan.isconnected():
        wifi_led.on()
        return True

    print("Connecting/Reconnecting to WiFi:", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wlan.isconnected() and retries > 0:
        wifi_led.toggle()
        time.sleep(0.5)
        print(".", end="")
        retries -= 1
    print()
    
    if wlan.isconnected():
        print("WiFi connected! IP:", wlan.ifconfig()[0])
        wifi_led.on()
        time.sleep(1)
        
        # Sync time with NTP
        ntp_success = False
        for server in ["pool.ntp.org", "time.google.com"]:
            try:
                print(f"Syncing time with NTP server ({server})...")
                ntptime.host = server
                ntptime.settime()
                ntp_success = True
                break
            except Exception as e:
                print(f"NTP sync failed for {server}: {e}")
                time.sleep(0.5)
                
        if ntp_success:
            try:
                # Calculate IST offset (UTC + 5:30)
                IST_OFFSET = (5 * 3600) + (30 * 60)
                ist_seconds = time.time() + IST_OFFSET
                tm = time.localtime(ist_seconds)
                
                # Set Pico RTC
                RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
                print("Time successfully calibrated to IST!")
            except Exception as e:
                print("Error setting RTC:", e)
        else:
            print("NTP sync skipped or failed. Using existing clock.")
        return True
    else:
        print("Failed to connect to WiFi. Proceeding offline...")
        wifi_led.off()
        return False

# =====================================================
# Send record to server
# =====================================================
def send_to_server(record):
    gc.collect()  # Free heap memory before HTTP connection
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Offline: Attempting reconnect before upload...")
        connect_wifi(retries=10)
        if not wlan.isconnected():
            print("Still offline: Skipping payload transmission.")
            return

    response = None
    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": API_KEY
        }
        response = urequests.post(SERVER_URL, data=json.dumps(record), headers=headers)
        print("Server Response:", response.status_code, response.text)
    except Exception as e:
        print("Send error:", e)
    finally:
        if response:
            response.close()  # Guarantees socket release
        gc.collect()

# =====================================================
# Sensor Reading Helpers
# =====================================================
def read_dht():
    for _ in range(3):
        try:
            dht_sensor.measure()
            t = dht_sensor.temperature()
            h = dht_sensor.humidity()
            if -40 <= t <= 80 and 0 <= h <= 100:
                return t, h
        except:
            pass
        time.sleep(1)
    print("DHT22 read failed. Using fallback value: 0.0")
    return 0.0, 0.0

def read_mq135(samples=10):
    try:
        total = 0
        for _ in range(samples):
            total += mq135.read_u16()
            time.sleep_ms(20)
        adc = total / samples
        voltage = (adc / 65535) * ADC_VREF
        if voltage < 0.01:
            voltage = 0.01
        
        # Calculate sensor resistance Rs
        rs = ((VCC_MQ - voltage) * RL) / voltage
        ratio = rs / R0
        return adc, voltage, rs, ratio
    except Exception as e:
        print("MQ135 hardware read failed:", e)
        return 0, 0.01, 999.0, 999.0

def ammonia_ppm(ratio):
    try:
        if ratio > 500: return 0.0
        ppm = 116.602 * (ratio ** -2.769)
        return round(max(0, ppm), 2)
    except:
        return 0.0

def h2s_ppm(ratio):
    try:
        if ratio > 500: return 0.0
        ppm = 25.0 * (ratio ** -1.5)
        return round(max(0, ppm), 2)
    except:
        return 0.0

# =====================================================
# WHI Penalty Calculations
# =====================================================
def nh3_penalty(ppm):
    if ppm <= 4: return 0
    elif ppm <= 4.3: return 7
    elif ppm <= 4.5: return 20
    elif ppm <= 5.2: return 30
    return 40

def h2s_penalty(ppm):
    if ppm <= 1: return 0
    elif ppm <= 3: return 1
    elif ppm <= 4.2: return 9
    elif ppm <= 4.6: return 16
    return 25

def humidity_penalty(h):
    if h == 0.0: return 0
    elif h <= 70: return 0
    elif h <= 86: return 2
    return 15

def temperature_penalty(t):
    if t == 0.0: return 0
    elif t <= 30: return 0
    elif t <= 32: return 10
    return 20

def calculate_whi_breakdown(avg_nh3, avg_h2s, avg_temp, avg_hum):
    p_nh3  = nh3_penalty(avg_nh3)
    p_h2s  = h2s_penalty(avg_h2s)
    p_hum  = humidity_penalty(avg_hum)
    p_temp = temperature_penalty(avg_temp)

    penalty = p_nh3 + p_h2s + p_hum + p_temp
    whi = max(0, min(100, 100 - penalty))

    return [whi, p_nh3, p_h2s, p_temp, p_hum]

def get_sensor_reading():
    temp, hum = read_dht()
    adc, voltage, rs, ratio = read_mq135()
    nh3 = ammonia_ppm(ratio)
    h2s = h2s_ppm(ratio)
    return {"temperature": temp, "humidity": hum, "nh3": nh3, "h2s": h2s}

def get_average_readings():
    print("------------------------------------")
    print("Reading 1...")
    print("------------------------------------")
    reading1 = get_sensor_reading()

    print("Temperature :", reading1["temperature"])
    print("Humidity    :", reading1["humidity"])
    print("NH3         :", reading1["nh3"])
    print("H2S         :", reading1["h2s"])

    print("\nWaiting 30 seconds (non-blocking)...\n")
    non_blocking_delay(30)

    print("------------------------------------")
    print("Reading 2...")
    print("------------------------------------")
    reading2 = get_sensor_reading()

    print("Temperature :", reading2["temperature"])
    print("Humidity    :", reading2["humidity"])
    print("NH3         :", reading2["nh3"])
    print("H2S         :", reading2["h2s"])

    avg_temp = round((reading1["temperature"] + reading2["temperature"]) / 2, 2)
    avg_hum  = round((reading1["humidity"] + reading2["humidity"]) / 2, 2)
    avg_nh3  = round((reading1["nh3"] + reading2["nh3"]) / 2, 2)
    avg_h2s  = round((reading1["h2s"] + reading2["h2s"]) / 2, 2)
    peak_nh3 = max(reading1["nh3"], reading2["nh3"])

    raw_whi, p_nh3, p_h2s, p_temp, p_hum = calculate_whi_breakdown(avg_nh3, avg_h2s, avg_temp, avg_hum)

    return {
        "avg_temperature_c": avg_temp,
        "avg_humidity_percent": avg_hum,
        "avg_nh3_ppm": avg_nh3,
        "peak_nh3_ppm": peak_nh3,
        "avg_h2s_ppm": avg_h2s,
        "raw_whi": raw_whi,
        "penalty_nh3": p_nh3,
        "penalty_h2s": p_h2s,
        "penalty_temperature": p_temp,
        "penalty_humidity": p_hum,
        "throughput": 0,
        "occupancy_inside": 0
    }

# =====================================================
# File Operations & Formatting
# =====================================================
def save_json(record):
    try:
        with open(JSON_FILE, "w") as file:
            json.dump(record, file)
    except Exception as e:
        print("JSON Save Error:", e)

def create_record(avg_data):
    t = RTC().datetime()
    
    timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        t[0], t[1], t[2], t[4], t[5], t[6]
    )

    return {
        "deviceId": deviceId,
        "timestamp": timestamp,
        "avg_nh3_ppm": round(avg_data["avg_nh3_ppm"], 2),
        "peak_nh3_ppm": round(avg_data["peak_nh3_ppm"], 2),
        "avg_h2s_ppm": round(avg_data["avg_h2s_ppm"], 2),
        "avg_temperature_c": round(avg_data["avg_temperature_c"], 2),
        "avg_humidity_percent": round(avg_data["avg_humidity_percent"], 2),
        "raw_whi": avg_data["raw_whi"],
        "penalty_nh3": avg_data["penalty_nh3"],
        "penalty_h2s": avg_data["penalty_h2s"],
        "penalty_temperature": avg_data["penalty_temperature"],
        "penalty_humidity": avg_data["penalty_humidity"],
        "throughput": 0,
        "occupancy_inside": 0
    }

# =====================================================
# Main Execution Cycle
# =====================================================
def process_cycle():
    wlan = network.WLAN(network.STA_IF)
    
    if not wlan.isconnected():
        print("WiFi connection lost. Attempting reconnect...")
        connect_wifi(retries=10)
    else:
        wifi_led.on()

    avg_data = get_average_readings()
    update_whi_leds(avg_data["raw_whi"])

    record = create_record(avg_data)
    save_json(record)

    print("\n========== FINAL DATA TO SEND ==========")
    print("Device ID :", record["deviceId"])
    print("Timestamp :", record["timestamp"])
    print("Avg Temp  :", record["avg_temperature_c"], "°C")
    print("Avg Hum   :", record["avg_humidity_percent"], "%")
    print("Avg NH3   :", record["avg_nh3_ppm"], "ppm")
    print("Peak NH3  :", record["peak_nh3_ppm"], "ppm")
    print("Avg H2S   :", record["avg_h2s_ppm"], "ppm")
    print("WHI       :", record["raw_whi"])
    print("========================================\n")

    send_to_server(record)

# =====================================================
# STARTUP & MAIN LOOP
# =====================================================
print("========================================")
print(" Intelligent Washroom Monitoring")
print(" Raspberry Pi Pico 2 W")
print(" Unique ID    :", deviceId)
print("========================================")

time.sleep(2)
connect_wifi()

while True:
    try:
        process_cycle()
        print("Waiting 30 seconds for next cycle...\n")
        non_blocking_delay(30)
        gc.collect()
    except KeyboardInterrupt:
        print("Program Stopped")
        wifi_led.off()
        green_led.on()  # Turn OFF in active-LOW
        red_led.on()    # Turn OFF in active-LOW
        break
    except Exception as e:
        print("Unexpected Error in loop:", e)
        non_blocking_delay(5)
