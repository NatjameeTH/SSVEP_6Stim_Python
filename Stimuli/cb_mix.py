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
    pygame.display.set_caption("SSVEP Checkerboard Mix Frequencies")

    # Stimulus state
    for stim in stimuli:
        stim["pos_xy"] = get_position(stim["pos"], screen_width, screen_height)
        stim["cell_freqs"] = []
        stim["cell_inverts"] = []
        stim["cell_last_flips"] = []
        stim["cell_intervals"] = []
        for row in range(rows):
            for col in range(cols):
                if (row + col) % 2 == 0:
                    f = stim["freqs"][0]
                else:
                    f = stim["freqs"][1]
                stim["cell_freqs"].append(f)
                stim["cell_inverts"].append(False)
                stim["cell_last_flips"].append(time.time())
                stim["cell_intervals"].append(1.0 / (2 * f))

    freq_pairs = [stim["freqs"] for stim in stimuli]
    random.shuffle(freq_pairs)

    trial_records = []
    stim_log = []
    trial_index = 1
    clock = pygame.time.Clock()

    sequence = []
    for pair in freq_pairs:
        sequence.append({"type": "fixation", "duration": 6})
        sequence.append({"type": "cue", "freqs": pair, "duration": 1})
        sequence.append({"type": "stim", "freqs": pair, "duration": 6})

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

        # Update flicker state
        for stim in stimuli:
            for i, f in enumerate(stim["cell_freqs"]):
                if current_time - stim["cell_last_flips"][i] >= stim["cell_intervals"][i]:
                    stim["cell_last_flips"][i] = current_time
                    stim["cell_inverts"][i] = not stim["cell_inverts"][i]

        # Sequence control (ครั้งเดียวต่อ frame)
        if step_index < len(sequence):
            step = sequence[step_index]

            if step["type"] == "fixation":
                draw_fixation_cross(screen, screen_width, screen_height)

            elif step["type"] == "cue":
                for stim in stimuli:
                    x_offset, y_offset = stim["pos_xy"]
                    # วาด stimulus แบบนิ่ง (ไม่ invert)
                    stim_copy = stim.copy()
                    stim_copy["cell_inverts"] = [False] * len(stim_copy["cell_inverts"])
                    draw_checkerboard_cells(screen, x_offset, y_offset, stim_copy)
                    draw_freq_label(screen, x_offset, y_offset, stim["freqs"])
                # วาดกรอบ highlight รอบ target
                for stim in stimuli:
                    if stim["freqs"] == step["freqs"]:
                        x, y = stim["pos_xy"]
                        draw_red_border(screen, x, y, board_width_px, board_height_px)

            elif step["type"] == "stim":
                for stim in stimuli:
                    x_offset, y_offset = stim["pos_xy"]
                    draw_checkerboard_cells(screen, x_offset, y_offset, stim)
                    draw_freq_label(screen, x_offset, y_offset, stim["freqs"])
                for stim in stimuli:
                    if stim["freqs"] == step["freqs"]:
                        x, y = stim["pos_xy"]
                        draw_red_border(screen, x, y, board_width_px, board_height_px)

            # Step timing
            if current_time - step_start >= step["duration"]:
                if step["type"] == "stim":
                    trial_records.append({
                        "trial_index": trial_index,
                        "freq": step["freqs"]   # ใช้ freqs ให้ตรงกับ sequence
                    })
                    stim_log.append(step["freqs"])
                    trial_index += 1   # เพิ่มลำดับทุกครั้งที่เจอ stim
                    elapsed_time = current_time - step_start
                    minutes = elapsed_time / 60.0
                    print(f"Stimulus {step['freqs']} Hz flickered for {minutes:.2f} minutes")
                step_index += 1
                step_start = current_time

        else:
            running = False

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()
    print("Stimulus order: CbMix", stim_log)
    # save_run_log("Checkerboard_Mixed", "P01", stim_log, trial_records)
    return stim_log, trial_records


if __name__ == "__main__":
    run()