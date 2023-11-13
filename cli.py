import serial
from threading import Thread
import traceback

class bcolors:
    KERNEL = '\033[94m'
    USER = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'


ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, parity="N")

def receive_messages():
    try:
        print(f"{bcolors.WARNING}Listening for messages...")

        while True:
            print(bcolors.USER)

            received_message = ser.read_until(expected=b"\0")

            formated = str(received_message, encoding="ascii")

            print(f"{bcolors.WARNING}received message:")

            print(f"{bcolors.KERNEL}{formated}")

    except TypeError:
        pass

    except:
        print(f"{bcolors.FAIL}\nError when trying to read messages:")

        traceback.print_exc()


t = Thread(target=receive_messages)

try:
    t.start()

    while True:
        print(bcolors.USER)

        user_message = input()

        if user_message == "~":
            print(f"{bcolors.WARNING}Erasing previous messages...")

            ser.write(b"~")

            continue

        if user_message == "^":
            print(f"{bcolors.WARNING}Getting read buffer contents...")

            ser.write(b"^")

            continue

        if user_message == "|":
            print(f"{bcolors.WARNING}Getting write buffer contents...")

            ser.write(b"|")

            continue

        ascii_bytes = (user_message + "\n").encode("ascii")

        ser.write(ascii_bytes)

        print(f"{bcolors.WARNING}Message was sent!")

except KeyboardInterrupt:
    print("\n")

except:
    print(f"{bcolors.FAIL}\nError when trying to write messages:")

    traceback.print_exc()

finally:
    print(f"{bcolors.WARNING}Closing connection...")

    ser.close()
