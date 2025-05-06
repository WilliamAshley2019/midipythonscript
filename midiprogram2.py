import mido
import serial
import threading
import time

SERIAL_PORT = 'COM3'
BAUDRATE = 31250

cc_to_mmc = {
    117: 'play',
    118: 'stop',
    119: 'record',
}

mmc_sysex = {
    'play': [0xF0, 0x7F, 0x7F, 0x06, 0x02, 0xF7],
    'stop': [0xF0, 0x7F, 0x7F, 0x06, 0x01, 0xF7],
    'record': [0xF0, 0x7F, 0x7F, 0x06, 0x06, 0xF7]
}

# Serial port
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
except serial.SerialException:
    ser = None
    print("Failed to open serial port")

# Prompt user for MIDI port selection
def choose_port(port_list, direction):
    print(f"\nAvailable {direction} MIDI ports:")
    for i, name in enumerate(port_list):
        print(f"{i}: {name}")
    index = int(input(f"Select {direction} port number: "))
    return port_list[index]

# Convert MIDI CC to MMC SysEx
def convert_cc_to_mmc(msg):
    if msg.type == 'control_change' and msg.control in cc_to_mmc:
        mmc_command = cc_to_mmc[msg.control]
        return mmc_sysex.get(mmc_command)
    return None

# Send SysEx over serial
def send_serial(data):
    if ser and ser.is_open:
        ser.write(bytes(data))

# USB MIDI listener
def midi_usb_listener(inport):
    print(f"Listening on USB MIDI: {inport.name}")
    for msg in inport:
        print("USB IN:", msg)
        sysex = convert_cc_to_mmc(msg)
        if sysex:
            print("Converted to MMC SysEx:", sysex)
            send_serial(sysex)

# RS232 serial listener
def serial_listener(outport):
    print("Listening on RS232...")
    buffer = bytearray()
    while True:
        if ser and ser.in_waiting:
            data = ser.read(ser.in_waiting)
            buffer.extend(data)
            while buffer and buffer[0] != 0xF0:
                byte = buffer.pop(0)
                print("RS232 IN Byte:", hex(byte))
            if buffer and buffer[0] == 0xF0:
                msg = []
                while buffer:
                    b = buffer.pop(0)
                    msg.append(b)
                    if b == 0xF7:
                        break
                print("RS232 IN SysEx:", msg)
                try:
                    outport.send(mido.Message.from_bytes(msg))
                except Exception as e:
                    print("Failed to send to USB:", e)
        time.sleep(0.01)

# Main logic
if __name__ == "__main__":
    inport_name = choose_port(mido.get_input_names(), "input")
    outport_name = choose_port(mido.get_output_names(), "output")

    inport = mido.open_input(inport_name)
    outport = mido.open_output(outport_name)

    # Start threads
    t1 = threading.Thread(target=midi_usb_listener, args=(inport,), daemon=True)
    t2 = threading.Thread(target=serial_listener, args=(outport,), daemon=True)
    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        if ser:
            ser.close()
