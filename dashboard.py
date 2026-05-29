import os
import sys
import math
import time
import random
import threading
import pygame
import serial

# ================= CONFIGURATION =================
# Hardware configuration
COM_PORT = 'COM9'
BAUD_RATE = 115200
FPS = 60
# =================================================

# Colors (Modern Sci-Fi Engineering Palette)
COLOR_DARK_BG = (15, 15, 18)        # Deep charcoal/almost black
COLOR_GRAPH_BG = (28, 28, 33)       # Matte charcoal gray for oscilloscope
COLOR_GRID_LINE = (42, 42, 48)      # Faded grid line
COLOR_TEXT_WHITE = (255, 255, 255)  # Pure White
COLOR_METER_BG = (22, 22, 26)       # Dark track for signal energy meter
COLOR_BORDER = (50, 50, 56)         # Cold gray border

# Matte State Panel Colors
COLOR_PANEL_STILL = (38, 166, 91)   # Soft matte forest green
COLOR_PANEL_MOVING = (230, 126, 34) # Solid safety orange
COLOR_PANEL_JUMPING = (192, 57, 43) # Solid crimson red

# State Variables
current_status = "STILL"            # Current status: STILL, MOVING, JUMPING
serial_connected = False
serial_obj = None
simulated_mode = False              # Keyboard override status flag

# Waveform history
wave_length = 680
wave_points = [0.0] * wave_length

# Background Serial Thread
def serial_reader_thread():
    global current_status, serial_connected, serial_obj, simulated_mode
    while True:
        if simulated_mode:
            time.sleep(0.5)
            continue
            
        if not serial_connected:
            try:
                serial_obj = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
                serial_connected = True
                print(f"Connected to ESP32 on {COM_PORT}!")
            except Exception:
                serial_connected = False
                time.sleep(2.0)
                continue

        try:
            if serial_obj and serial_obj.in_waiting > 0:
                line = serial_obj.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    upper_line = line.upper()
                    if "STILL" in upper_line or "0" in upper_line:
                        current_status = "STILL"
                    elif "MOVING" in upper_line or "1" in upper_line:
                        current_status = "MOVING"
                    elif "JUMPING" in upper_line or "2" in upper_line:
                        current_status = "JUMPING"
        except Exception:
            print("Serial communication lost. Reconnecting...")
            serial_connected = False
            if serial_obj:
                try:
                    serial_obj.close()
                except:
                    pass
            time.sleep(1.0)

# Initialize Serial Thread
thread = threading.Thread(target=serial_reader_thread, daemon=True)
thread.start()

def get_meter_color(pct):
    """Interpolate between Green -> Orange -> Red based on percentage."""
    if pct < 0.35:
        # Green to Yellow-Green
        r = int(pct / 0.35 * 200)
        g = 255
        b = 50
    elif pct < 0.7:
        # Yellow to Orange
        r = 255
        g = int(255 - ((pct - 0.35) / 0.35 * 135))
        b = 0
    else:
        # Orange to Red
        r = 255
        g = int(120 - ((pct - 0.7) / 0.3 * 100))
        b = int((pct - 0.7) / 0.3 * 50)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def main():
    global current_status, serial_connected, simulated_mode
    
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("ESP32 HAR: Edge Data Cockpit")
    
    window_w = 900
    window_h = 800
    screen = pygame.display.set_mode((window_w, window_h))
    clock = pygame.time.Clock()
    
    # Futuristic crisp scaled fonts
    try:
        font_main_status = pygame.font.Font(None, 46)  # Reduced from 82 to prevent text overflow in the bottom panel
        font_panel_hdr = pygame.font.Font(None, 20)    # Slightly reduced for a cleaner spacing
        font_meter_lbl = pygame.font.Font(None, 20)
        font_header_txt = pygame.font.Font(None, 28)
        font_warning = pygame.font.Font(None, 52)
        font_warn_sub = pygame.font.Font(None, 22)
    except:
        font_main_status = pygame.font.SysFont("courier", 36, bold=True)  # Reduced from 72 for fallback safety
        font_panel_hdr = pygame.font.SysFont("courier", 15, bold=True)
        font_meter_lbl = pygame.font.SysFont("courier", 14, bold=True)
        font_header_txt = pygame.font.SysFont("courier", 22, bold=True)
        font_warning = pygame.font.SysFont("courier", 42, bold=True)
        font_warn_sub = pygame.font.SysFont("courier", 15)

    # 1. Oscilloscope bounds (70% height section)
    osc_x = 30
    osc_y = 50
    osc_w = 680
    osc_h = 500
    
    # 2. Variance Meter bounds
    meter_x = 750
    meter_y = 50
    meter_w = 120
    meter_h = 500
    
    # Signal statistics parameters
    noise_phase = 0.0

    running = True
    while running:
        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    current_status = "STILL"
                    simulated_mode = True
                elif event.key == pygame.K_m:
                    current_status = "MOVING"
                    simulated_mode = True
                elif event.key == pygame.K_j:
                    current_status = "JUMPING"
                    simulated_mode = True
                elif event.key == pygame.K_r:
                    simulated_mode = False
                    serial_connected = False

        # Generate live oscilloscope values matching hardware behavior
        noise_phase += 0.25
        if current_status == "STILL":
            new_val = math.sin(noise_phase) * 1.5 + random.uniform(-0.5, 0.5)
        elif current_status == "MOVING":
            new_val = (
                math.sin(noise_phase) * 20.0 + 
                math.sin(noise_phase * 2.3) * 15.0 + 
                random.uniform(-10.0, 10.0)
            )
        elif current_status == "JUMPING":
            # Highly erratic spiky waveform
            if random.random() > 0.65:
                new_val = random.choice([-150.0, 150.0]) + random.uniform(-20.0, 20.0)
            else:
                new_val = math.sin(noise_phase * 3.5) * 60.0 + random.uniform(-20.0, 20.0)
        
        # Shift and load waveform array
        wave_points.append(new_val)
        if len(wave_points) > wave_length:
            wave_points.pop(0)

        # 3. Calculate Immediate Waveform Variance (Signal Energy)
        # Using rolling std deviation of the last 30 samples
        recent_pts = wave_points[-30:]
        recent_mean = sum(recent_pts) / len(recent_pts)
        variance = sum((x - recent_mean) ** 2 for x in recent_pts) / len(recent_pts)
        std_dev = math.sqrt(variance)
        
        # Map variance (0 to 60) to fill percentage (0.0 to 1.0)
        energy_pct = min(1.0, std_dev / 60.0)

        # Rendering
        screen.fill(COLOR_DARK_BG)

        # --- A. Draw Oscilloscope Card ---
        # Card outline and background
        pygame.draw.rect(screen, COLOR_GRAPH_BG, (osc_x, osc_y, osc_w, osc_h))
        pygame.draw.rect(screen, COLOR_BORDER, (osc_x, osc_y, osc_w, osc_h), 2)
        
        # Subtle grid system (lines every 50 pixels)
        for grid_x in range(osc_x + 50, osc_x + osc_w, 50):
            pygame.draw.line(screen, COLOR_GRID_LINE, (grid_x, osc_y), (grid_x, osc_y + osc_h), 1)
        for grid_y in range(osc_y + 50, osc_y + osc_h, 50):
            pygame.draw.line(screen, COLOR_GRID_LINE, (osc_x, grid_y), (osc_x + osc_w, grid_y), 1)
            
        # Draw central baseline horizontal line
        pygame.draw.line(screen, (70, 70, 80), (osc_x, osc_y + osc_h // 2), (osc_x + osc_w, osc_y + osc_h // 2), 1)

        # Generate waveform coordinates
        points_to_draw = []
        for idx, val in enumerate(wave_points):
            px = osc_x + idx
            # Inverse val so positive peaks go upward on the screen
            py = osc_y + (osc_h // 2) - int(val)
            # Clip bounds to keep line strictly inside the graph card
            py = max(osc_y + 2, min(osc_y + osc_h - 2, py))
            points_to_draw.append((px, py))
            
        # Plot anti-aliased line for high-res crispness
        if len(points_to_draw) >= 2:
            line_color = (0, 255, 230) # High contrast neon cyan
            for idx in range(len(points_to_draw) - 1):
                pygame.draw.aaline(screen, line_color, points_to_draw[idx], points_to_draw[idx + 1])

        # Header for the oscilloscope
        lbl_graph_hdr = font_panel_hdr.render("LIVE CSI WAVEFORM (ANTI-ALIASED)", True, (130, 135, 140))
        screen.blit(lbl_graph_hdr, (osc_x + 10, osc_y - 25))

        # --- B. Draw Live Signal Energy Meter Bar ---
        # Outer track card
        pygame.draw.rect(screen, COLOR_METER_BG, (meter_x, meter_y, meter_w, meter_h))
        pygame.draw.rect(screen, COLOR_BORDER, (meter_x, meter_y, meter_w, meter_h), 2)
        
        # Calculate dynamic fill
        padding = 10
        inner_w = meter_w - (padding * 2)
        inner_max_h = meter_h - (padding * 2) - 40 # Reserve top 40px for percentage label
        
        fill_h = int(energy_pct * inner_max_h)
        fill_y = meter_y + meter_h - padding - fill_h
        
        # Get dynamic color
        meter_color = get_meter_color(energy_pct)
        
        # Draw fill bar
        if fill_h > 0:
            pygame.draw.rect(screen, meter_color, (meter_x + padding, fill_y, inner_w, fill_h))
            
        # Draw a subtle grid/tick overlays on the meter
        for tick in range(1, 10):
            tick_y = meter_y + meter_h - padding - int((tick / 10.0) * inner_max_h)
            pygame.draw.line(screen, COLOR_DARK_BG, (meter_x + padding, tick_y), (meter_x + meter_w - padding, tick_y), 2)

        # Render dynamic signal energy text label
        lbl_energy_txt = font_meter_lbl.render("ENERGY", True, (130, 135, 140))
        lbl_pct = font_header_txt.render(f"{int(energy_pct * 100)}%", True, meter_color)
        
        screen.blit(lbl_energy_txt, (meter_x + meter_w // 2 - lbl_energy_txt.get_width() // 2, meter_y + 10))
        screen.blit(lbl_pct, (meter_x + meter_w // 2 - lbl_pct.get_width() // 2, meter_y + 25))

        # Header for the meter
        lbl_meter_hdr = font_panel_hdr.render("SIGNAL ENERGY", True, (130, 135, 140))
        screen.blit(lbl_meter_hdr, (meter_x + meter_w // 2 - lbl_meter_hdr.get_width() // 2, meter_y - 25))

        # --- C. Minimalist State Readout (30% Height bottom section) ---
        panel_x = 30
        panel_y = 580
        panel_w = 840
        panel_h = 190
        
        # Match colors and blink state
        if current_status == "STILL":
            panel_color = COLOR_PANEL_STILL
        elif current_status == "MOVING":
            panel_color = COLOR_PANEL_MOVING
        else: # JUMPING
            # Blinking alert background for JUMPING status
            blink = int(time.time() * 5) % 2
            panel_color = COLOR_PANEL_JUMPING if blink == 1 else (60, 10, 15)

        # Draw solid matte background card
        pygame.draw.rect(screen, panel_color, (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, COLOR_BORDER, (panel_x, panel_y, panel_w, panel_h), 2)
        
        # Draw status panel headers
        lbl_card_hdr = font_panel_hdr.render("CLASSIFIED ACTIVITY REAL-TIME EDGE PREDICTION", True, (230, 240, 230))
        screen.blit(lbl_card_hdr, (panel_x + 20, panel_y + 15))
        
        # Map internal status strings to professional user display labels
        label_map = {
            "STILL": "STATIC BASELINE",
            "MOVING": "DYNAMIC MOTION",
            "JUMPING": "HIGH-INTENSITY TRANSIENT"
        }
        ui_status_label = label_map.get(current_status, current_status)
        
        # Massive futuristic text indicator
        if current_status == "JUMPING":
            # For flashing alert box in JUMPING state, coordinate the text blinking with background
            status_text = f"CLASSIFIED STATE: {ui_status_label}" if blink == 1 else "CLASSIFIED STATE: "
        else:
            status_text = f"CLASSIFIED STATE: {ui_status_label}"
            
        lbl_main = font_main_status.render(status_text, True, COLOR_TEXT_WHITE)
        screen.blit(
            lbl_main, 
            (panel_x + panel_w // 2 - lbl_main.get_width() // 2, 
             panel_y + panel_h // 2 - lbl_main.get_height() // 2 + 10)
        )
        
        # Simulation Mode Overlay warning text
        if simulated_mode:
            lbl_sim_alert = font_panel_hdr.render("SIMULATION OVERRIDE ACTIVE. PRESS [R] TO CLEAR AND RESUME ESP32 HARDWARE SCAN.", True, (255, 255, 0))
            screen.blit(lbl_sim_alert, (panel_x + panel_w // 2 - lbl_sim_alert.get_width() // 2, panel_y + panel_h - 25))
        else:
            lbl_sim_alert = font_panel_hdr.render("KEYBOARD HOTKEYS: [S]TATIC BASELINE, [M]OTION (DYNAMIC), [J]UMPING (TRANSIENT) TO SIMULATE WAVES", True, (220, 220, 220))
            screen.blit(lbl_sim_alert, (panel_x + panel_w // 2 - lbl_sim_alert.get_width() // 2, panel_y + panel_h - 25))

        # --- D. Full-Screen Hardware Warning Overlay ---
        if not serial_connected and not simulated_mode:
            warn_surf = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
            # Semi-transparent backdrop overlay
            pygame.draw.rect(warn_surf, (10, 12, 10, 230), (0, 0, window_w, window_h))
            
            # Pulsing color warnings
            pulse = int(math.sin(time.time() * 5) * 127 + 128)
            pulse_color = (255, pulse, 50)
            
            # Box panel
            pygame.draw.rect(warn_surf, COLOR_DARK_BG, (100, 220, 700, 360))
            pygame.draw.rect(warn_surf, pulse_color, (100, 220, 700, 360), 2)
            
            lbl_warn = font_warning.render("WAITING FOR HARDWARE...", True, pulse_color)
            lbl_warn_sub = font_warn_sub.render(
                f"Ensure the ESP32 is connected via USB and mapping to '{COM_PORT}' in dashboard.py",
                True, (180, 185, 180)
            )
            lbl_warn_or = font_warn_sub.render(
                "Press [S], [M], or [J] on your keyboard to launch offline Simulation Mode!",
                True, (0, 200, 255)
            )
            
            # Align centered
            warn_surf.blit(lbl_warn, (100 + 350 - lbl_warn.get_width() // 2, 280))
            warn_surf.blit(lbl_warn_sub, (100 + 350 - lbl_warn_sub.get_width() // 2, 380))
            warn_surf.blit(lbl_warn_or, (100 + 350 - lbl_warn_or.get_width() // 2, 440))
            
            screen.blit(warn_surf, (0, 0))

        # Refresh
        pygame.display.flip()
        clock.tick(FPS)

    # Quit
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
