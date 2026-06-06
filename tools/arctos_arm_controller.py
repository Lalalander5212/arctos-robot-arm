"""
Arctos Arm Controller GUI

Team project note:
This GUI controller was developed by a teammate and used during testing
to send serial commands to the Arduino-based robotic arm system.

My main contributions to the project were hardware assembly, servo integration,
Arduino-based servo testing, and mechanical troubleshooting.
"""

import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

# ── Serial connection ──────────────────────────────────
ser = None

def get_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

def connect():
    global ser
    port = port_var.get()
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        status_var.set(f"Connected to {port}")
        status_label.config(fg="#2ecc71")
    except Exception as e:
        status_var.set(f"Failed: {e}")
        status_label.config(fg="#e74c3c")

def send_command(cmd):
    if ser and ser.is_open:
        ser.write((cmd + "\n").encode())
        log(f">> {cmd}")
    else:
        log("Not connected to Arduino.")

def log(msg):
    output.config(state="normal")
    output.insert("end", msg + "\n")
    output.see("end")
    output.config(state="disabled")

# ── Undo history ───────────────────────────────────────
# Each entry is a list of (type, value) tuples representing one full action
# type is "axis" with value (axis_letter, steps) or "gripper" with value (prev_degrees)
undo_stack = []
prev_gripper = 40  # tracks last gripper position so we know where to return to

def push_undo(actions):
    undo_stack.append(actions)
    undo_btn.config(state="normal")

def undo():
    if not undo_stack:
        return

    actions = undo_stack.pop()
    parts = []

    for action_type, value in actions:
        if action_type == "axis":
            axis, steps = value
            reverse = -steps  # flip the sign to go backwards
            parts.append(f"{axis}{reverse}")
        elif action_type == "gripper":
            prev = value  # value is where the gripper was before the move
            parts.append(f"GRIPPER {prev}")
            # update the slider and label to reflect the restored position
            gripper_var.set(prev)
            grip_val_label.config(text=f"{prev}°")

    if parts:
        cmd = " ".join(parts)
        send_command(cmd)
        log(f"↩ Undo: {cmd}")

    if not undo_stack:
        undo_btn.config(state="disabled")

# ── Movement ───────────────────────────────────────────
def move_axis(axis, steps):
    if steps == 0:
        log("Nothing to move — slider is at 0.")
        return
    push_undo([("axis", (axis, steps))])
    send_command(f"{axis}{steps}")

def move_gripper(degrees):
    global prev_gripper
    push_undo([("gripper", prev_gripper)])  # save where we were before moving
    prev_gripper = degrees
    send_command(f"GRIPPER {degrees}")

def send_all():
    global prev_gripper
    actions = []

    x = x_var.get()
    y = y_var.get()
    z = z_var.get()
    g = gripper_var.get()

    parts = []

    if x != 0:
        parts.append(f"X{x}")
        actions.append(("axis", ("X", x)))
    if y != 0:
        parts.append(f"Y{y}")
        actions.append(("axis", ("Y", y)))
    if z != 0:
        parts.append(f"Z{z}")
        actions.append(("axis", ("Z", z)))

    # always include gripper in send all
    actions.append(("gripper", prev_gripper))
    parts.append(f"GRIPPER {g}")
    prev_gripper = g

    if parts:
        push_undo(actions)
        send_command(" ".join(parts))

# ── Build UI ───────────────────────────────────────────
root = tk.Tk()
root.title("Arctos Arm Controller")
root.configure(bg="#1e1e2e")
root.resizable(False, False)

DARK   = "#1e1e2e"
PANEL  = "#2a2a3e"
ACCENT = "#7c6af7"
TEXT   = "#cdd6f4"
MUTED  = "#6c7086"
GREEN  = "#2ecc71"
RED    = "#e74c3c"

def styled_frame(parent, **kw):
    return tk.Frame(parent, bg=PANEL, bd=0, relief="flat", **kw)

def styled_button(parent, text, cmd, color=ACCENT):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg="white", font=("Segoe UI", 10, "bold"),
                     relief="flat", bd=0, padx=14, pady=6,
                     activebackground="#5a4fcf", activeforeground="white",
                     cursor="hand2")

# ── Header ─────────────────────────────────────────────
header = tk.Frame(root, bg=ACCENT, pady=12)
header.pack(fill="x")
tk.Label(header, text="Arctos Arm Controller", bg=ACCENT, fg="white",
         font=("Segoe UI", 16, "bold")).pack()

# ── Connection bar ─────────────────────────────────────
conn_frame = tk.Frame(root, bg=DARK, pady=10)
conn_frame.pack(fill="x", padx=20, pady=(12, 0))

tk.Label(conn_frame, text="Port:", bg=DARK, fg=TEXT,
         font=("Segoe UI", 10)).pack(side="left", padx=(0, 6))

port_var = tk.StringVar()
ports = get_ports()
port_var.set(ports[0] if ports else "")
port_menu = ttk.Combobox(conn_frame, textvariable=port_var,
                          values=ports, width=12, state="readonly")
port_menu.pack(side="left", padx=(0, 8))

styled_button(conn_frame, "Connect", connect).pack(side="left", padx=(0, 16))

status_var = tk.StringVar(value="Not connected")
status_label = tk.Label(conn_frame, textvariable=status_var, bg=DARK,
                         fg=RED, font=("Segoe UI", 10, "italic"))
status_label.pack(side="left")

def refresh_ports():
    ports = get_ports()
    port_menu["values"] = ports
    if ports:
        port_var.set(ports[0])

styled_button(conn_frame, "↻", refresh_ports, color=MUTED).pack(side="right")

# ── Axis sliders ───────────────────────────────────────
sliders_frame = tk.Frame(root, bg=DARK, pady=8)
sliders_frame.pack(fill="x", padx=20, pady=10)

def make_axis_slider(parent, label, var, from_, to, axis, row, color):
    card = styled_frame(parent, pady=10, padx=14)
    card.grid(row=row, column=0, sticky="ew", pady=5)
    parent.columnconfigure(0, weight=1)

    header_row = tk.Frame(card, bg=PANEL)
    header_row.pack(fill="x")

    tk.Label(header_row, text=label, bg=PANEL, fg=color,
             font=("Segoe UI", 13, "bold")).pack(side="left")
    val_label = tk.Label(header_row, text="0 steps", bg=PANEL, fg=MUTED,
                          font=("Segoe UI", 10))
    val_label.pack(side="right")

    def on_change(v):
        val_label.config(text=f"{int(float(v))} steps")

    slider = tk.Scale(card, variable=var, from_=from_, to=to,
                      orient="horizontal", bg=PANEL, fg=TEXT,
                      troughcolor="#3a3a5e", highlightthickness=0,
                      activebackground=color, sliderrelief="flat",
                      bd=0, length=460, showvalue=False,
                      command=on_change)
    slider.pack(fill="x", pady=(6, 0))

    btn_row = tk.Frame(card, bg=PANEL)
    btn_row.pack(fill="x", pady=(8, 0))
    styled_button(btn_row, f"Move {label}",
                  lambda a=axis, v=var: move_axis(a, v.get()),
                  color=color).pack(side="left")
    styled_button(btn_row, "Zero",
                  lambda v=var, l=val_label: [v.set(0), l.config(text="0 steps")],
                  color=MUTED).pack(side="left", padx=8)

x_var = tk.IntVar(value=0)
y_var = tk.IntVar(value=0)
z_var = tk.IntVar(value=0)

make_axis_slider(sliders_frame, "X Axis", x_var, -6000,  6000,  "X", 0, "#f38ba8")
make_axis_slider(sliders_frame, "Y Axis", y_var, -15000, 15000, "Y", 1, "#a6e3a1")
make_axis_slider(sliders_frame, "Z Axis", z_var, -20000, 20000, "Z", 2, "#89b4fa")

# ── Gripper slider ─────────────────────────────────────
grip_card = styled_frame(root, pady=10, padx=14)
grip_card.pack(fill="x", padx=20, pady=(0, 10))

grip_header = tk.Frame(grip_card, bg=PANEL)
grip_header.pack(fill="x")
tk.Label(grip_header, text="Gripper", bg=PANEL, fg="#fab387",
         font=("Segoe UI", 13, "bold")).pack(side="left")
grip_val_label = tk.Label(grip_header, text="40°", bg=PANEL, fg=MUTED,
                           font=("Segoe UI", 10))
grip_val_label.pack(side="right")

gripper_var = tk.IntVar(value=40)

def on_grip_change(v):
    grip_val_label.config(text=f"{int(float(v))}°")

grip_slider = tk.Scale(grip_card, variable=gripper_var, from_=40, to=170,
                        orient="horizontal", bg=PANEL, fg=TEXT,
                        troughcolor="#3a3a5e", highlightthickness=0,
                        activebackground="#fab387", sliderrelief="flat",
                        bd=0, length=460, showvalue=False,
                        command=on_grip_change)
grip_slider.pack(fill="x", pady=(6, 0))

grip_btn_row = tk.Frame(grip_card, bg=PANEL)
grip_btn_row.pack(fill="x", pady=(8, 0))
styled_button(grip_btn_row, "Move Gripper",
              lambda: move_gripper(gripper_var.get()), color="#fab387").pack(side="left")
styled_button(grip_btn_row, "Close (170°)",
              lambda: [gripper_var.set(170), grip_val_label.config(text="170°"),
                       move_gripper(170)], color=MUTED).pack(side="left", padx=8)
styled_button(grip_btn_row, "Open (30°)",
              lambda: [gripper_var.set(30), grip_val_label.config(text="30°"),
                       move_gripper(30)], color=MUTED).pack(side="left")

# ── Send all + Undo row ────────────────────────────────
action_frame = tk.Frame(root, bg=DARK, pady=6)
action_frame.pack(fill="x", padx=20)

styled_button(action_frame, "▶  Send All Axes + Gripper",
              send_all, color=ACCENT).pack(side="left", fill="x", expand=True,
                                           ipady=6, padx=(0, 8))

undo_btn = styled_button(action_frame, "↩  Undo", undo, color="#e74c3c")
undo_btn.pack(side="left", ipady=6)
undo_btn.config(state="disabled")  # greyed out until there's something to undo

# ── Output log ─────────────────────────────────────────
log_frame = tk.Frame(root, bg=DARK)
log_frame.pack(fill="both", expand=True, padx=20, pady=(10, 16))

tk.Label(log_frame, text="Command log", bg=DARK, fg=MUTED,
         font=("Segoe UI", 9)).pack(anchor="w")

output = tk.Text(log_frame, height=7, bg=PANEL, fg=TEXT,
                  font=("Cascadia Code", 9), relief="flat",
                  state="disabled", wrap="word",
                  insertbackground=TEXT)
output.pack(fill="both", expand=True)

root.mainloop()