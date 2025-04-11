from flask import Flask, render_template
from flask_socketio import SocketIO
import RPi.GPIO as GPIO
import time
import eventlet
import threading

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)
#socketio = SocketIO(app, async_mode='threading')
#socketio = SocketIO(app, async_mode='eventlet')

# GPIO nastavení (upraveno - STBY pryč, AIN2 na pin 27)
MOTOR_PINS = {
    "AIN1": 22,
    "AIN2": 17,  # přehodíme z pinu 17, ten byl zároveň STBY
    "BIN1": 24,
    "BIN2": 23
}

PWM_PINS = {
    "PWMA": 18,
    "PWMB": 25
}

# Výchozí rychlost
speed = 100

GPIO.setmode(GPIO.BCM)

# Inicializace pinů
for pin in PWM_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

for pin in MOTOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Inicializace PWM
pwmA = GPIO.PWM(PWM_PINS["PWMA"], 1000)
pwmB = GPIO.PWM(PWM_PINS["PWMB"], 1000)

pwmA.start(0)
pwmB.start(0)

def gradual_start(pwm, target_speed, step=5, delay=0.02):
    """ Postupné zrychlování motoru na požadovanou rychlost """
    for dc in range(0, target_speed + 1, step):
        pwm.ChangeDutyCycle(dc)
        time.sleep(delay)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('motor_command')
def handle_motor_command(data):
    global speed
    command = data.get('command', '')
    new_speed = data.get('speed')

    if new_speed is not None:
        speed = new_speed

    # Zastavení motorů
    for pin in MOTOR_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    if command == "forward":
        GPIO.output(MOTOR_PINS["AIN1"], GPIO.HIGH)
        GPIO.output(MOTOR_PINS["BIN1"], GPIO.HIGH)
        threading.Thread(target=gradual_start, args=(pwmA, speed)).start()
        threading.Thread(target=gradual_start, args=(pwmB, speed)).start()
    elif command == "backward":
        GPIO.output(MOTOR_PINS["AIN2"], GPIO.HIGH)
        GPIO.output(MOTOR_PINS["BIN2"], GPIO.HIGH)
        threading.Thread(target=gradual_start, args=(pwmA, speed)).start()
        threading.Thread(target=gradual_start, args=(pwmB, speed)).start()
    elif command == "left":
        GPIO.output(MOTOR_PINS["AIN1"], GPIO.HIGH)
        GPIO.output(MOTOR_PINS["BIN2"], GPIO.HIGH)
        threading.Thread(target=gradual_start, args=(pwmA, speed)).start()
        threading.Thread(target=gradual_start, args=(pwmB, speed)).start()
    elif command == "right":
        GPIO.output(MOTOR_PINS["AIN2"], GPIO.HIGH)
        GPIO.output(MOTOR_PINS["BIN1"], GPIO.HIGH)
        threading.Thread(target=gradual_start, args=(pwmA, speed)).start()
        threading.Thread(target=gradual_start, args=(pwmB, speed)).start()

    socketio.emit('response', {'status': f'Motor {command} at {speed}% speed'})

@socketio.on('speed_change')
def handle_speed_change(data):
    global speed
    speed = data.get('speed', 100)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)
    socketio.emit('response', {'status': f'Speed changed to {speed}%'})

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        try:
            pwmA.stop()
            pwmB.stop()
        except Exception as e:
            print("PWM stop error:", e)
        GPIO.cleanup()
