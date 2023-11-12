import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import serial
from threading import Thread
import traceback
from time import sleep

ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, parity="N")

def send_receive_request(log = print):
    try:
        while True:
            ser.write(b"`")

            sleep(1)

    except TypeError:
        pass

    except serial.PortNotOpenError:
        pass

    except:
        log("Error when trying to send receive request!")

        traceback.print_exc()

def receive_messages(log = print):
    last_message = ""

    try:
        log(f"Listening for messages from '{ser.port }'...")

        while True:
            received_message = ser.read_until(expected=b"\0")

            formated = str(received_message, encoding="ascii")

            if last_message == formated:
                continue

            last_message = formated

            log(f"Received message: {formated}")

    except TypeError:
        pass

    except:
        log("Error when trying to read messages!")

        traceback.print_exc()


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Pi UART Client", default_width=700, default_height=900)
        self.set_border_width(10)

        t = Thread(target=receive_messages, args=[self.log])
        t_timer = Thread(target=send_receive_request, args=[self.log])

        self.send_button = Gtk.Button(label="Send")
        self.send_button.connect("clicked", self.on_send)

        self.echo_back_button = Gtk.Button(label="Echo Back")
        self.echo_back_button.connect("clicked", self.on_echo_back)

        self.clear_button = Gtk.Button(label="Clear")
        self.clear_button.connect("clicked", self.on_clear)

        self.received_messagens_view = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.CHAR)

        scroll_window = Gtk.ScrolledWindow(child=self.received_messagens_view)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        grid.attach(self.send_button, 0, 0, 1, 1)
        grid.attach_next_to(self.echo_back_button, self.send_button, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.clear_button, self.echo_back_button, Gtk.PositionType.BOTTOM, 1, 1)

        box = Gtk.Box(spacing=10)
        box.pack_start(grid, False, False, 0)
        box.pack_start(scroll_window, True, True, 0)

        self.add(box)

        t.start()
        t_timer.start()

    def log(self, text = ""):
        old_buffer = self.received_messagens_view.get_buffer()

        old_text = old_buffer.get_text(old_buffer.get_start_iter(), old_buffer.get_end_iter(), True)

        new_text = old_text + ">" + text + "\n"

        new_buffer = Gtk.TextBuffer()

        new_buffer.set_text(new_text)

        self.received_messagens_view.set_buffer(new_buffer)

    def on_send(self, widget):
        user_message = "Igor de Almeida"

        ascii_bytes = (user_message + "\n").encode("ascii")

        ser.write(ascii_bytes)

        self.log("Message was sent!")

    def on_echo_back(self, widget):
        self.log("Getting write buffer contents...")

        ser.write(b"^")

    def on_clear(self, widget):
        new_text = ""

        new_buffer = Gtk.TextBuffer()

        new_buffer.set_text(new_text)

        self.received_messagens_view.set_buffer(new_buffer)


def window_quit(arg):
    Gtk.main_quit(arg)

    print("Closing connection...")

    ser.close()

win = MyWindow()
win.connect("destroy", window_quit)
win.show_all()
Gtk.main()
