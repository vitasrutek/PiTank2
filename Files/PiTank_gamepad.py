from evdev import InputDevice, categorize, ecodes, list_devices
import RPi.GPIO as GPIO
import time

time.sleep(2)

# Nastavení GPIO
enA = 18  # PWM motor 1
enB = 25  # PWM motor 2
IN1 = 17
IN2 = 22
IN3 = 23
IN4 = 24

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#GPIO.setup([enA, enB, IN1, IN2, IN3, IN4], GPIO.OUT)
for pin in [enA, enB, IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)

pwmA = GPIO.PWM(enA, 100)  # Motor 1
pwmB = GPIO.PWM(enB, 100)  # Motor 2
pwmA.start(0)
pwmB.start(0)

# Najdi DS4 zařízení
devices = [InputDevice(path) for path in list_devices()]
for device in devices:
    print(device.name, device.path)

# Vyber správné zařízení
gamepad = InputDevice('/dev/input/event2')  # Nahraď správnou cestou

# Funkce pro ovládání motorů
def drive_motors(speed, turn):
    # Výpočet rychlostí pro levý a pravý motor
    left_speed = speed + turn
    right_speed = speed - turn

    # Omezení rychlostí na rozsah -100 až 100
    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))

    # Tolerance kolem hodnoty 127 (pokud hodnota páčky je mezi 125 a 130, považujeme to za střed)
    neutral_zone = 5  # Tolerance pro střední pozici
    if abs(left_speed) < neutral_zone and abs(right_speed) < neutral_zone:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        return

    # Levý motor
    if left_speed > 0:  # Vpřed
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif left_speed < 0:  # Vzad
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    else:  # Stop
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(abs(left_speed))

    # Pravý motor
    if right_speed > 0:  # Vpřed
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    elif right_speed < 0:  # Vzad
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    else:  # Stop
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
    pwmB.ChangeDutyCycle(abs(right_speed))


# Výchozí rychlosti
speed = 0  # Vpřed/vzad
turn = 0   # Otáčení

print("Listening to gamepad inputs...")
for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:
        absevent = categorize(event)

        # Debug: Zobrazíme všechny hodnoty z gamepadu
        print(f"Event code: {absevent.event.code}, Value: {absevent.event.value}")

        # Levá páčka: ABS_Y → rychlost (vpřed/vzad)
        if absevent.event.code == ecodes.ABS_Y:
            speed = int((128 - absevent.event.value) * 100 / 128)
            print(f"Speed: {speed}")

        # Ignorujeme horizontální pohyb levé páčky (ABS_X)
        elif absevent.event.code == ecodes.ABS_X:
            if abs(absevent.event.value) > 10:  # Pokud je hodnota ne-nulová, ignorujeme ji
                continue

        # Pravá páčka: ABS_X (nebo případně ABS_RX) → otáčení (doprava/doleva)
        elif absevent.event.code == ecodes.ABS_X or absevent.event.code == ecodes.ABS_RX:
            turn = int((absevent.event.value - 128) * 100 / 128)
            print(f"Turn: {turn}")

        # Ovládání motorů
        drive_motors(speed, turn)
