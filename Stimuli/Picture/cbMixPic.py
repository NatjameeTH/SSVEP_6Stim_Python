import pygame
import sys
import time
import random
import csv
import datetime
import tkinter as tk
from tkinter import filedialog

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

# === Parameters ===
rows, cols = 4, 5
square_size_cm = 1
pixels_per_cm = 30

square_size_px = int(square_size_cm * pixels_per_cm)
board_width_px = cols * square_size_px
board_height_px = rows * square_size_px

# Stimuli definition (แต่ละ checkerboard มีคู่ความถี่)
stimuli = [
    {"freqs": (7, 14), "pos": "top-center"},
    {"freqs": (8, 16), "pos": "center-right"},
    {"freqs": (13, 26), "pos": "center-down"},
    {"freqs": (6, 18), "pos": "center-left"},
    {"freqs": (15, 7.5), "pos": "center"},
]

# === Positioning function ===
def get_position(pos_label, screen_width, screen_height):
    margin = int(2 * pixels_per_cm)
    if pos_label == "top-center":
        x = (screen_width - board_width_px) // 2
        y = margin
    elif pos_label == "center-right":
        x = screen_width - board_width_px - margin
        y = (screen_height - board_height_px) // 2
    elif pos_label == "center-left":
        x = margin
        y = (screen_height - board_height_px) // 2
    elif pos_label == "center-down":
        x = (screen_width - board_width_px) // 2
        y = screen_height - board_height_px - margin
    elif pos_label == "center":
        x = (screen_width - board_width_px) // 2
        y = (screen_height - board_height_px) // 2
    else:
        x, y = 0, 0
    return x, y

# === Function to draw checkerboard with per-cell frequencies ===
def draw_checkerboard_cells(screen, x_offset, y_offset, stim):
    idx = 0
    for row in range(rows):
        for col in range(cols):
            invert = stim["cell_inverts"][idx]
            if (row + col) % 2 == 0:
                color = (255,255,255) if not invert else (0,0,0)
            else:
                color = (0,0,0) if not invert else (255,255,255)
            rect = pygame.Rect(
                x_offset + col * square_size_px,
                y_offset + row * square_size_px,
                square_size_px,
                square_size_px,
            )
            pygame.draw.rect(screen, color, rect)
            idx += 1

# === Function to draw fixation cross ===
def draw_fixation_cross(screen, screen_width, screen_height):
    cross_length = int(1 * pixels_per_cm)
    center_x = screen_width // 2
    center_y = screen_height // 2
    pygame.draw.line(screen, (0, 0, 0),
                     (center_x - cross_length, center_y),
                     (center_x + cross_length, center_y), 5)
    pygame.draw.line(screen, (0, 0, 0),
                     (center_x, center_y - cross_length),
                     (center_x, center_y + cross_length), 5)

# === Function to draw border ===
def draw_red_border(screen, x_offset, y_offset, width, height):
    border_rect = pygame.Rect(x_offset -5  , y_offset - 5, width + 10, height + 10)
    pygame.draw.rect(screen, (0, 0, 255), border_rect, 4)

# === Function to draw frequency label ===
def draw_freq_label(screen, x_offset, y_offset, freqs):
    font = pygame.font.SysFont("Times New Roman", 15)
    text = font.render(f"{freqs[0]}, {freqs[1]} Hz", True, (0, 0, 0))
    text_rect = text.get_rect(center=(x_offset + board_width_px // 2,
                                      y_offset + board_height_px + 20))
    screen.blit(text, text_rect)

# === Main run function ===
def run():
    pygame.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Static Checkerboards")

    for stim in stimuli:
        stim["pos_xy"] = get_position(stim["pos"], screen_width, screen_height)

    clock = pygame.time.Clock()
    running = True
    saved = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        screen.fill((160, 160, 160))

        # วาด checkerboard แบบคงที่
        for stim in stimuli:
            x_offset, y_offset = stim["pos_xy"]
            stim_copy = stim.copy()
            stim_copy["cell_inverts"] = [False] * (rows * cols)
            draw_checkerboard_cells(screen, x_offset, y_offset, stim_copy)
            draw_freq_label(screen, x_offset, y_offset, stim["freqs"])

        pygame.display.flip()
        clock.tick(60)

        if not saved:
            pygame.image.save(screen, "cbMixPic.png")
            print("Saved static checkerboard to checkerboard_static.png")
            saved = True

    pygame.quit()

if __name__ == "__main__":
    run()