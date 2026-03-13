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
    print(f"Stimulus log saved to {file_path}")

# === Parameters ===
rows, cols = 4, 5
square_size_cm = 1
pixels_per_cm = 30

square_size_px = int(square_size_cm * pixels_per_cm)
board_width_px = cols * square_size_px
board_height_px = rows * square_size_px
circle_radius_px = 2
num_circles = 160

# === Stimuli definition (ความถี่ผสม) ===
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

# === Generate non-overlapping circle positions ===
def generate_poisson_circles(n, width, height, radius, min_dist=None):
    if min_dist is None:
        min_dist = 3.5 * radius + 1
    positions = []
    attempts = 0
    max_attempts = 100000
    while len(positions) < n and attempts < max_attempts:
        x = random.randint(radius, width - radius)
        y = random.randint(radius, height - radius)
        valid = True
        for (px, py) in positions:
            dist = math.hypot(x - px, y - py)
            if dist < min_dist:
                valid = False
                break
        if valid:
            positions.append((x, y))
        attempts += 1
    #print(f"Generated {len(positions)} circles with Poisson-like spacing.")
    return positions

# === Draw circle pattern with two frequencies ===
def draw_circle_pattern_twofreq(screen, x_offset, y_offset, positions, invert_flags):
    black_count, white_count = 0, 0
    for i, (x, y) in enumerate(positions):
        if i < num_circles // 2:   # ครึ่งแรกใช้ freq1
            invert = invert_flags[0]
            color = (0,0,0) if not invert else (255,255,255)
            black_count += 1
        else:                      # ครึ่งหลังใช้ freq2
            invert = invert_flags[1]
            color = (255,255,255) if not invert else (0,0,0)
            white_count += 1

        pygame.gfxdraw.aacircle(screen, x_offset+x, y_offset+y, circle_radius_px, color)
        pygame.gfxdraw.filled_circle(screen, x_offset+x, y_offset+y, circle_radius_px, color)

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
def draw_freq_label(screen, x_offset, y_offset, freqs):
    font = pygame.font.SysFont("Times New Roman", 12)
    text = font.render(f"{freqs[0]}, {freqs[1]} Hz", True, (0, 0, 0))
    text_rect = text.get_rect(center=(x_offset + board_width_px // 2,
                                      y_offset + board_height_px + 20))
    screen.blit(text, text_rect)

# === Draw highlight border ===
def draw_highlight_border(screen, x_offset, y_offset, width, height):
    border_rect = pygame.Rect(x_offset - 5, y_offset - 5, width + 10, height + 10)
    pygame.draw.rect(screen, (0, 0, 255), border_rect, 4)

def run():
    pygame.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Static Circle Stimuli")

    for stim in stimuli:
        stim["pos_xy"] = get_position(stim["pos"], screen_width, screen_height)
        stim["positions"] = generate_poisson_circles(num_circles, board_width_px, board_height_px, circle_radius_px)

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

        # วาดวงกลมแบบคงที่
        for stim in stimuli:
            x, y = stim["pos_xy"]
            draw_circle_pattern_twofreq(screen, x, y, stim["positions"], [False, False])
            draw_freq_label(screen, x, y, stim["freqs"])

        pygame.display.flip()
        clock.tick(60)

        if not saved:
            pygame.image.save(screen, "dot160Mix.png")
            print("Saved static circles to circles_static.png")
            saved = True

    pygame.quit()

if __name__ == "__main__":
    run()