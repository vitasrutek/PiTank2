from flask import Flask, render_template
from flask_socketio import SocketIO
import RPi.GPIO as GPIO

app = Flask(__name__)
socketio = SocketIO(app)

# Nastavení GPIO pinů (přizpůsobeno pro TB6612FNG)
MOTOR_PINS = {
    "AIN1": 22,  # Levý pás dopředu
    "AIN2": 17,  # Levý pás dozadu
    "BIN1": 24,  # Pravý pás dopředu
    "BIN2": 23,  # Pravý pás dozadu
    "STBY": 17   # Standby pro aktivaci driveru
}

PWM_PINS = {
    "PWMA": 18,  # PWM pro levý motor
    "PWMB": 25   # PWM pro pravý motor
}

# Výchozí rychlost
speed = 100  # 100 % výkonu

GPIO.setmode(GPIO.BCM)

# Inicializace PWM pinů
for pin in PWM_PINS.values():
    GPIO.setup(pin, GPIO.OUT)  # Nastavení pinu jako výstup

# Inicializace výstupů
for pin in MOTOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Aktivace STBY
GPIO.output(MOTOR_PINS["STBY"], GPIO.HIGH)

# Inicializace PWM pinů
pwmA = GPIO.PWM(PWM_PINS["PWMA"], 1000)  # 1 kHz
pwmB = GPIO.PWM(PWM_PINS["PWMB"], 1000)

pwmA.start(0)
pwmB.start(0)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('motor_command')
def handle_motor_command(data):
    global speed
    command = data.get('command', '')
    new_speed = data.get('speed')  # Tady už neber výchozí hodnotu 100

    if new_speed is not None:  # Pokud přijde nová rychlost, změň ji
        speed = new_speed

    # Zastavení motorů
    GPIO.output(MOTOR_PINS["AIN1"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["AIN2"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["BIN1"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["BIN2"], GPIO.LOW)

    # Ovládání směru podle příkazu
    if command == "forward":
        GPIO.output(MOTOR_PINS["AIN1"], GPIO.HIGH)  # Levý pás dopředu
        GPIO.output(MOTOR_PINS["BIN1"], GPIO.HIGH)  # Pravý pás dopředu
    elif command == "backward":
        GPIO.output(MOTOR_PINS["AIN2"], GPIO.HIGH)  # Levý pás dozadu
        GPIO.output(MOTOR_PINS["BIN2"], GPIO.HIGH)  # Pravý pás dozadu
    elif command == "left":
        GPIO.output(MOTOR_PINS["AIN2"], GPIO.HIGH)  # Levý pás dozadu
        GPIO.output(MOTOR_PINS["BIN1"], GPIO.HIGH)  # Pravý pás dopředu
    elif command == "right":
        GPIO.output(MOTOR_PINS["AIN1"], GPIO.HIGH)  # Levý pás dopředu
        GPIO.output(MOTOR_PINS["BIN2"], GPIO.HIGH)  # Pravý pás dozadu

    # Nastavení PWM
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

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
        pwmA.stop()
        pwmB.stop()
        GPIO.cleanup()
