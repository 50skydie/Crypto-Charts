import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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

    print(f"Days Before: {days_before_val}, Prediction in Days: {prediction_days_val}")



# ---------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------
root = tk.Tk()
root.title("Prediction Dashboard")
root.geometry("900x500")
root.configure(bg="#f0f0f0")

# ---------------------------------------------------------------------
# Frame Setup
# ---------------------------------------------------------------------
frame_left = ttk.Frame(root, width=600, height=500, relief=tk.SUNKEN)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
frame_right = ttk.Frame(root, width=300, height=500)
frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

# ---------------------------------------------------------------------
# Matplotlib Graph Placeholder
# ---------------------------------------------------------------------
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.plot([1, 2, 3, 4], [10, 20, 25, 22])  # Example data
ax.set_title("Sample Data Plot")

canvas = FigureCanvasTkAgg(fig, master=frame_left)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------------------------------------------------------------------
# Input Fields & Controls
# ---------------------------------------------------------------------
# Days Before
label_days_before = ttk.Label(frame_right, text="Days Before:")
label_days_before.pack(pady=(50, 5))
entry_days_before = ttk.Entry(frame_right, width=25)
entry_days_before.pack(pady=5)

# Prediction in Days
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

# Optional result label placeholder (if you want to display results on UI)
result_label = ttk.Label(frame_right, text="", font=("Arial", 10, "bold"))
result_label.pack(pady=(20, 5))

# ---------------------------------------------------------------------
# Run Tkinter Main Loop
# ---------------------------------------------------------------------
root.mainloop()