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

# Flicker frequencies (Hz) และตำแหน่ง
stimuli = [
    {"freq": 7, "pos": "top-center"},
    {"freq": 8, "pos": "center-right"},
    {"freq": 13, "pos": "center-down"},
    {"freq": 6, "pos": "center-left"},
    {"freq": 15, "pos": "center"},
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

# === Drawing functions (ย่อไว้) ===
def draw_checkerboard(screen, x_offset, y_offset, invert=False):
    for row in range(rows):
        for col in range(cols):
            if (row + col) % 2 == 0:
                color = (255, 255, 255) if not invert else (0, 0, 0)
            else:
                color = (0, 0, 0) if not invert else (255, 255, 255)
            rect = pygame.Rect(
                x_offset + col * square_size_px,
                y_offset + row * square_size_px,
                square_size_px,
                square_size_px,
            )
            pygame.draw.rect(screen, color, rect)

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

def draw_red_border(screen, x_offset, y_offset, width, height):
    border_rect = pygame.Rect(x_offset - 5, y_offset - 5, width + 10, height + 10)
    pygame.draw.rect(screen, (0, 0, 255), border_rect, 4)

def draw_freq_label(screen, x_offset, y_offset, freq):
    font = pygame.font.SysFont("Times New Roman", 15)
    text = font.render(f"{freq} Hz", True, (0, 0, 0))
    text_rect = text.get_rect(
        center=(x_offset + board_width_px // 2,
                y_offset + board_height_px + 20)
    )
    screen.blit(text, text_rect)

# === Main run function ===
def run():
    pygame.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("SSVEP Flicker Checkerboards")

    # Stimulus state
    for stim in stimuli:
        stim["invert"] = False
        stim["last_flip"] = time.time()
        stim["interval"] = 1.0 / (2 * stim["freq"])
        stim["pos_xy"] = get_position(stim["pos"], screen_width, screen_height)

    freqs = [stim["freq"] for stim in stimuli]
    random.shuffle(freqs)

    stim_log = []
    trial_records = []
    trial_index = 1

    # Sequence: fixation (6s), stim (6s)
    sequence = []
    for freq in freqs:
        sequence.append({"type": "fixation", "freq": freq, "duration": 6})
        sequence.append({"type": "stim", "freq": freq, "duration": 6})

    clock = pygame.time.Clock()
    step_index = 0
    step_start = time.time()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        screen.fill((128, 128, 128))
        current_time = time.time()

        # Update flicker state only during stim
        if step_index < len(sequence):
            step = sequence[step_index]
            if step["type"] == "stim":
                for stim in stimuli:
                    if current_time - stim["last_flip"] >= stim["interval"]:
                        stim["invert"] = not stim["invert"]
                        stim["last_flip"] = current_time

        if step_index < len(sequence):
            step = sequence[step_index]

            if step["type"] == "fixation":
                draw_fixation_cross(screen, screen_width, screen_height)

            elif step["type"] == "stim":
                elapsed = current_time - step_start

                if elapsed < 1.0:
                    # 1 วินาทีแรก: วาด checkerboard คงที่ + กรอบ
                    for stim in stimuli:
                        x_offset, y_offset = stim["pos_xy"]
                        draw_checkerboard(screen, x_offset, y_offset, invert=False)
                        draw_freq_label(screen, x_offset, y_offset, stim["freq"])
                    # กรอบไฮไลท์รอบ target
                    for stim in stimuli:
                        if stim["freq"] == step["freq"]:
                            x, y = stim["pos_xy"]
                            draw_red_border(screen, x, y, board_width_px, board_height_px)

                else:
                    # หลัง 1 วินาที: checkerboard กระพริบ + กรอบ
                    for stim in stimuli:
                        x_offset, y_offset = stim["pos_xy"]
                        draw_checkerboard(screen, x_offset, y_offset, stim["invert"])
                        draw_freq_label(screen, x_offset, y_offset, stim["freq"])
                    # กรอบไฮไลท์รอบ target
                    for stim in stimuli:
                        if stim["freq"] == step["freq"]:
                            x, y = stim["pos_xy"]
                            draw_red_border(screen, x, y, board_width_px, board_height_px)
           
            if current_time - step_start >= step["duration"]:
                if step["type"] == "stim":
                    trial_records.append({
                        "trial_index": trial_index,
                        "freq": step["freq"]
                    })
                    stim_log.append(step["freq"])
                    trial_index += 1

                step_index += 1
                step_start = current_time
        else:
            running = False

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()
    print("Stimulus order: CbSingle", stim_log)
    #save_run_log("CbSingle", trial_records)
    return stim_log, trial_records

if __name__ == "__main__":
    run()