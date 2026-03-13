import tkinter as tk
import pygame
import csv
import datetime
from tkinter import filedialog
from Stimuli import (
    cb_single,
    cb_mix,
    dot160_single,
    dot160_mix,
    dot80_single,
    dot80_mix,
)

pygame.display.set_caption("SSVEP Flicker Checkerboards")

# === Function to save CSV ===
def save_run_log(run_name, participant_id, stim_log, trial_records):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save stimulus log"
    )
    if not file_path:
        print("User cancelled save.")
        return

    with open(file_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        # Run-level info
        writer.writerow(["Run name", run_name])
        writer.writerow(["Participant ID", participant_id])
        writer.writerow(["Run timestamp", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
        writer.writerow([])

        # Trial-level info (เหลือเฉพาะ Trial ID และ Frequency)
        writer.writerow(["Trial ID", "Frequency"])
        for rec in trial_records:
            writer.writerow([
                rec["trial_index"],
                rec["freq"]
            ])
    print(f"Stimulus log saved to {file_path}")

# === Functions to launch stimulus modules ===
def launch_pattern(pattern):
    freq_window = tk.Toplevel(root)
    freq_window.title(f"{pattern} - Select Frequency")
    freq_window.geometry("300x200")

    label = tk.Label(freq_window, text=f"Select Frequency Type for {pattern}", font=("Arial", 12))
    label.pack(pady=20)

    def run_fundamental():
        if pattern == "Checkerboard":
            stim_log, trial_records = cb_single.run()
            save_run_log("Checkerboard_Fundamental", "P01", stim_log, trial_records)
        elif pattern == "Dot 160":
            stim_log, trial_records = dot160_single.run()
            save_run_log("Dot160_Fundamental", "P01", stim_log, trial_records)
        elif pattern == "Dot 80":
            stim_log, trial_records = dot80_single.run()
            save_run_log("Dot80_Fundamental", "P01", stim_log, trial_records)
        freq_window.destroy()

    def run_mixed():
        if pattern == "Checkerboard":
            stim_log, trial_records = cb_mix.run()
            save_run_log("Checkerboard_Mixed", "P01", stim_log, trial_records)
        elif pattern == "Dot 160":
            stim_log, trial_records = dot160_mix.run()
            save_run_log("Dot160_Mixed", "P01", stim_log, trial_records)
        elif pattern == "Dot 80":
            stim_log, trial_records = dot80_mix.run()
            save_run_log("Dot80_Mixed", "P01", stim_log, trial_records)
        freq_window.destroy()

    tk.Button(freq_window, text="Fundamental Frequency", width=25, command=run_fundamental).pack(pady=5)
    tk.Button(freq_window, text="Mixed Frequencies", width=25, command=run_mixed).pack(pady=5)

def exit_app():
    root.destroy()
# === Tkinter GUI ===
root = tk.Tk()
root.title("Stimulus Selector")
root.geometry("300x300")

tk.Label(root, text="Select Stimulus Pattern", font=("Arial", 14)).pack(pady=20)

tk.Button(root, text="Checkerboard", width=20, command=lambda: launch_pattern("Checkerboard")).pack(pady=5)
tk.Button(root, text="Dot 160", width=20, command=lambda: launch_pattern("Dot 160")).pack(pady=5)
tk.Button(root, text="Dot 80", width=20, command=lambda: launch_pattern("Dot 80")).pack(pady=5)

tk.Button(root, text="Exit", width=20, command=exit_app).pack(pady=20)

root.mainloop()