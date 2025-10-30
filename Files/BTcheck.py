#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess
import signal

# --- MAC adresa ovladače ---
TARGET_MAC = "XX_XX_XX_XX_XX" # edit yourself

# --- sem si uložíme běžící proces ---
running_proc = None

def device_property_changed(interface, changed, invalidated, path):
    global running_proc

    if interface != "org.bluez.Device1":
        return

    if not path.endswith(TARGET_MAC):
        return

    if "Connected" in changed:
        if changed["Connected"]:
            print(f"{TARGET_MAC} se připojilo — spouštím PiTank_gamepad.py")
            # Spustíme jen pokud ještě neběží
            if running_proc is None or running_proc.poll() is not None:
                running_proc = subprocess.Popen(["python3", "/home/X/PiTank_gamepad.py"])  # edit correct path
        else:
            print(f"{TARGET_MAC} se odpojilo — ukončuji PiTank_gamepad.py")
            if running_proc and running_proc.poll() is None:
                running_proc.terminate()
                try:
                    running_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    running_proc.kill()
                running_proc = None

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
bus.add_signal_receiver(
    device_property_changed,
    bus_name="org.bluez",
    signal_name="PropertiesChanged",
    path_keyword="path"
)

print("Sleduji připojení a odpojení Bluetooth zařízení...")
GLib.MainLoop().run()
