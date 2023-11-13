import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import serial
from threading import Thread, Lock
import traceback
from time import sleep

mutex = Lock()

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

            if formated.startswith("Max buffer size") and formated == last_message:
                continue

            last_message = formated

            log(formated, "Kernel")

    except TypeError:
        pass

    except:
        log("Error when trying to read messages!")

        traceback.print_exc()


class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, text="", source=""):
        super().__init__()

        label = Gtk.Label()

        span_style = ""

        if source == "Client":
            span_style = 'foreground="black" size="large"'
            label.set_halign(Gtk.Align.END)
        elif source == "Kernel":
            span_style = 'foreground="blue" size="large"'
            label.set_halign(Gtk.Align.START)
        else:
            span_style = 'foreground="red" size="large"'
            label.set_halign(Gtk.Align.CENTER)

        markup = "<markup>"

        for line in text.split("\n"):
            new_line = line.rstrip("\0")

            markup += f'\n<span {span_style}>{new_line}</span>'

        markup += "\n</markup>"

        label.set_markup(markup)

        self.add(label)

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Pi UART Client", default_width=600, default_height=900)
        self.set_border_width(10)

        t = Thread(target=receive_messages, args=[self.log])
        t_timer = Thread(target=send_receive_request, args=[self.log])

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

        self.log_list = Gtk.ListBox()
        self.log_list.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll_window = Gtk.ScrolledWindow(child=self.log_list)

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
        t_timer.start()

    def log(self, text = "", source = ""):
        with mutex:
            self.log_list.add(ListBoxRowWithData(text, source))
            self.log_list.show_all()

    def on_send(self, widget):
        user_message = self.entry.get_text()

        ascii_bytes = (user_message + "\n").encode("ascii")

        ser.write(ascii_bytes)

        self.log(user_message, "Client")

    def on_echo_back(self, widget):
        ser.write(b"^")

    def on_read(self, widget):
        ser.write(b"`")

    def on_clear_history(self, widget):
        ser.write(b"~")

    def on_clear_log(self, widget):
        with mutex:
            children = self.log_list.get_children()

            for element in children:
                self.log_list.remove(element)

            self.log_list.show_all()

try:
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

except Exception:
    traceback.print_exc()

finally:
    print("Closing connection...")
    ser.close()