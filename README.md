# PiTank2
RC printed tank powered by Raspberry Pi Zero2

<img src="https://github.com/vitasrutek/PiTank2/blob/main/Screenshot.jpg" width="250">

Flask script for tank built almost from scratch.  
Python3 file for engine control and HTML for frontend mainly for touchscreen devices (ontouchstart event).  
Front camera is simple PiCamera2 mjpeg server.  
Engines has smooth start forward and turns with speed control (slider in HTML).  
dependencies:  
```
sudo apt install python3-flask python3-eventlet python3-gpiozero python3-socketio python3
```

Or run second Python3 file for RC via bluetooth gamepad like DS4 (controller has to be paired and connected via bluetoothctl (or etc.)).  
dependencies:  
```
sudo apt install evtest   # run for find correct evdev ID
pip3 install evdev
```
### Parts
- Raspberry Pi Zero2 W (with "spy" camera module)
- USB powerbank (single 3,7V cell)
- 7,4V battery cell from some RC car
- TB6612FNG dual motor driver (much less power consumption than L298N) - [example link](https://www.laskakit.cz/dvoumotorovy-radic-tb6612fng/)
- 2x JGA25-370 6V with 1320RPM - [example link](https://www.laskakit.cz/motor-jga25-370-6v-s-prevodovkou-/?variantId=7734/)
- 8x 608RS2 bearing


![zapojeni](https://github.com/vitasrutek/PiTank2/blob/main/Zapojeni.png)

<table>
  <tr>
    <th><img src="https://github.com/vitasrutek/PiTank2/blob/main/PiTank1.png" width="250"></th>
    <th><img src="https://github.com/vitasrutek/PiTank2/blob/main/PiTank2.png" width="250"></th>
  </tr>

</table>
