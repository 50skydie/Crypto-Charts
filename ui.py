#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from logic import fetch_btc_price_for_x_days, plot_with_forecast
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def on_calculate():
    days_before = entry_days_before.get().strip()
    prediction_days = entry_prediction_days.get().strip()

    if not days_before or not prediction_days:
        warning_label.config(
            text="⚠️ Both fields are required!", foreground="red"
        )
        return

    warning_label.config(text="")

    try:
        days_before_val = int(days_before)
        prediction_days_val = int(prediction_days)
    except ValueError:
        warning_label.config(
            text="⚠️ Please enter valid numbers only!", foreground="red"
        )
        return

    btc_data = fetch_btc_price_for_x_days(days_before_val)
    if btc_data is None:
        messagebox.showerror("Error", "Failed to fetch BTC data.")
        return

    fig = plot_with_forecast(btc_data, prediction_days_val)

    for widget in frame_left.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_left)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def on_close():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        print("Exiting application...")
        root.destroy()
        os._exit(0)


# Main UI setup
root = tk.Tk()
root.title("Prediction Dashboard")
root.geometry("1200x600")
root.configure(bg="#f0f0f0")
root.protocol("WM_DELETE_WINDOW", on_close)

frame_left = ttk.Frame(root, width=900, height=600, relief=tk.SUNKEN)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_right = ttk.Frame(root, width=300, height=600)
frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

# Days Before Input
label_days_before = ttk.Label(frame_right, text="Historical in Days:")
label_days_before.pack(pady=(50, 5))
entry_days_before = ttk.Entry(frame_right, width=25)
entry_days_before.pack(pady=5)

# Prediction in Days Input
label_prediction_days = ttk.Label(frame_right, text="Prediction in Days:")
label_prediction_days.pack(pady=(20, 5))
entry_prediction_days = ttk.Entry(frame_right, width=25)
entry_prediction_days.pack(pady=5)

# Warning Label
warning_label = ttk.Label(frame_right, text="", foreground="red")
warning_label.pack(pady=(10, 10))

# Calculate Button
btn_calculate = ttk.Button(frame_right, text="Calculate", command=on_calculate)
btn_calculate.pack(pady=(20, 10))

root.mainloop()