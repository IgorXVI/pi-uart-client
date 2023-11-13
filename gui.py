import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import serial
from threading import Thread
import traceback

ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, parity="N")

def receive_messages(log = print):
    try:
        log(f"Listening for messages from '{ser.port }'...")

        while True:
            received_message = ser.read_until(expected=b"\0")

            formated = str(received_message, encoding="ascii")

            log(f"Received message:\n{formated}")

    except TypeError:
        pass

    except:
        log("Error when trying to read messages!")

        traceback.print_exc()


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Pi UART Client", default_width=600, default_height=900)
        self.set_border_width(10)

        t = Thread(target=receive_messages, args=[self.log])

        self.entry = Gtk.Entry()
        self.entry.set_text("Message from client.")

        self.send_button = Gtk.Button(label="Send")
        self.send_button.connect("clicked", self.on_send)

        self.echo_back_button = Gtk.Button(label="Read Message History")
        self.echo_back_button.connect("clicked", self.on_echo_back)

        self.read_button = Gtk.Button(label="Read Kernel Messages")
        self.read_button.connect("clicked", self.on_read)

        self.clear_history_button = Gtk.Button(label="Clear History")
        self.clear_history_button.connect("clicked", self.on_clear_history)

        self.clear_log_button = Gtk.Button(label="Clear Log")
        self.clear_log_button.connect("clicked", self.on_clear_log)

        self.received_messagens_view = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.CHAR)

        scroll_window = Gtk.ScrolledWindow(child=self.received_messagens_view)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        grid.attach(self.entry, 0, 0, 3, 1)
        grid.attach_next_to(self.send_button, self.entry, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.echo_back_button, self.entry, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.read_button, self.echo_back_button, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.clear_history_button, self.read_button, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.clear_log_button, self.clear_history_button, Gtk.PositionType.RIGHT, 1, 1)

        box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(grid, False, False, 0)
        box.pack_start(scroll_window, True, True, 0)

        self.add(box)

        t.start()

    def log(self, text = ""):
        old_buffer = self.received_messagens_view.get_buffer()

        old_text = old_buffer.get_text(old_buffer.get_start_iter(), old_buffer.get_end_iter(), True)

        new_text = f"{old_text}->{text}\n"

        new_buffer = Gtk.TextBuffer()

        new_buffer.set_text(new_text)

        self.received_messagens_view.set_buffer(new_buffer)

    def on_send(self, widget):
        user_message = self.entry.get_text()

        ascii_bytes = (user_message + "\n").encode("ascii")

        ser.write(ascii_bytes)

        self.log(f"Message '{user_message}' was sent!")

    def on_echo_back(self, widget):
        ser.write(b"^")

    def on_read(self, widget):
        ser.write(b"`")

    def on_clear_history(self, widget):
        ser.write(b"~")

    def on_clear_log(self, widget):
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
