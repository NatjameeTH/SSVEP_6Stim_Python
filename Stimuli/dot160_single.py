import pygame
import sys
import time
import random
import math
import pygame.gfxdraw
import csv
import datetime
import tkinter as tk
from tkinter import filedialog

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
    #print(f"Stimulus log saved to {file_path}")

# === Parameters ===
rows, cols = 4, 5
square_size_cm = 1
pixels_per_cm = 30

square_size_px = int(square_size_cm * pixels_per_cm)
board_width_px = cols * square_size_px
board_height_px = rows * square_size_px
circle_radius_px = 2
num_circles = 160

# === Stimuli definition ===
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

# === Generate non-overlapping circle positions ===
def generate_nonoverlapping_circles(n, width, height, radius):
    positions = []
    max_attempts = 50000
    attempts = 0
    while len(positions) < n and attempts < max_attempts:
        x = random.randint(radius, width - radius)
        y = random.randint(radius, height - radius)
        valid = True
        for (px, py) in positions:
            dist = math.hypot(x - px, y - py)
            if dist < 2 * radius + 2:  # buffer กันชน
                valid = False
                break
        if valid:
            positions.append((x, y))
        attempts += 1
    return positions

# === Draw randomized circle pattern ===
def draw_circle_pattern(screen, x_offset, y_offset, positions, invert=False):
    black_count, white_count = 0, 0
    for i, (x, y) in enumerate(positions):
        if i < num_circles // 2:  # 80 วงแรกเป็นสีดำ
            color = (0, 0, 0) if not invert else (255, 255, 255)
        else:                     # 80 วงหลังเป็นสีขาว
            color = (255, 255, 255) if not invert else (0, 0, 0)

        if color == (0, 0, 0):
            black_count += 1
        else:
            white_count += 1

        pygame.gfxdraw.aacircle(screen, x_offset + x, y_offset + y, circle_radius_px, color)
        pygame.gfxdraw.filled_circle(screen, x_offset + x, y_offset + y, circle_radius_px, color)

    # ✅ print จำนวนที่วาดจริง
    #print(f"Stimulus drawn: Black={black_count}, White={white_count}, Total={black_count+white_count}")

# === Partial shuffle ===
def partial_shuffle(positions, fraction=0.2):
    n = len(positions)
    k = int(n * fraction)
    for _ in range(k):
        i, j = random.sample(range(n), 2)
        positions[i], positions[j] = positions[j], positions[i]
    return positions

# === Draw fixation cross ===
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

# === Draw frequency label ===
def draw_freq_label(screen, x_offset, y_offset, freq):
    font = pygame.font.SysFont("Times New Roman", 12)
    text = font.render(f"{freq} Hz", True, (0, 0, 0))
    text_rect = text.get_rect(center=(x_offset + board_width_px // 2,
                                      y_offset + board_height_px + 20))
    screen.blit(text, text_rect)

# === Draw highlight border ===
def draw_highlight_border(screen, x_offset, y_offset, width, height):
    border_rect = pygame.Rect(x_offset - 5, y_offset - 5, width + 10, height + 10)
    pygame.draw.rect(screen, (0, 0, 255), border_rect, 4)

# === Main run function ===
def run():
    pygame.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("SSVEP Random Circle Flicker")

    # Stimulus state
    for stim in stimuli:
        stim["invert"] = False
        stim["last_flip"] = time.time()
        stim["interval"] = 1.0 / (2 * stim["freq"])
        stim["pos_xy"] = get_position(stim["pos"], screen_width, screen_height)
        stim["positions"] = generate_nonoverlapping_circles(num_circles, board_width_px, board_height_px, circle_radius_px)

    # สุ่มลำดับความถี่
    freqs = [stim["freq"] for stim in stimuli]
    random.shuffle(freqs)

    # Sequence: fixation (6s) → stim (6s)
    sequence = []
    for freq in freqs:
        sequence.append({"type": "fixation", "duration": 6})
        sequence.append({"type": "stim", "freq": freq, "duration": 6})

    stim_log = []
    trial_records = []
    trial_index = 1
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
                    # 1 วินาทีแรก: วาดวงกลมคงที่ + กรอบ
                    for stim in stimuli:
                        x, y = stim["pos_xy"]
                        draw_circle_pattern(screen, x, y, stim["positions"], invert=False)
                        draw_freq_label(screen, x, y, stim["freq"])
                    # กรอบไฮไลท์
                    for stim in stimuli:
                        if stim["freq"] == step["freq"]:
                            x, y = stim["pos_xy"]
                            draw_highlight_border(screen, x, y, board_width_px, board_height_px)

                else:
                    # หลัง 1 วินาที: วาดวงกลมพร้อมกระพริบ + กรอบ
                    for stim in stimuli:
                        x, y = stim["pos_xy"]
                        draw_circle_pattern(screen, x, y, stim["positions"], stim["invert"])
                        draw_freq_label(screen, x, y, stim["freq"])
                    # กรอบไฮไลท์
                    for stim in stimuli:
                        if stim["freq"] == step["freq"]:
                            x, y = stim["pos_xy"]
                            draw_highlight_border(screen, x, y, board_width_px, board_height_px)
                
            # Step timing
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
    print("Stimulus order: Dot160Sing", stim_log)
    # save_run_log("Dot160Sing", "P01", stim_log, trial_records)
    return stim_log, trial_records

if __name__ == "__main__":
    run()