import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import butter, filtfilt
import tkinter as tk

def trajectory_heatmap_slider():
    # --- CONFIGURATION ---
    WINDOW_1_W_PCT = 0.5  
    WINDOW_2_W_PCT = 0.4  
    WINDOW_H_PCT = 0.8
    # ---------------------

    print("1. Loading Data...")
    try:
        # Load Linear Acceleration
        df_lin = pd.read_csv('Linear Acceleration.csv')
        t_col = [c for c in df_lin.columns if 'Time' in c][0]
        x_col = [c for c in df_lin.columns if 'x' in c and 'Acceleration' in c][0]
        y_col = [c for c in df_lin.columns if 'y' in c and 'Acceleration' in c][0]
        
        t = df_lin[t_col].values
        ax = df_lin[x_col].values
        ay = df_lin[y_col].values
        
        # Load Magnetometer
        try:
            df_mag = pd.read_csv('Magnetometer.csv')
            mag_t_col = [c for c in df_mag.columns if 'Time' in c][0]
            mag_x_col = [c for c in df_mag.columns if 'x' in c and 'field' in c][0]
            mag_y_col = [c for c in df_mag.columns if 'y' in c and 'field' in c][0]
            mag_z_col = [c for c in df_mag.columns if 'z' in c and 'field' in c][0]
            
            mag_x = np.interp(t, df_mag[mag_t_col], df_mag[mag_x_col])
            mag_y = np.interp(t, df_mag[mag_t_col], df_mag[mag_y_col])
            mag_z = np.interp(t, df_mag[mag_t_col], df_mag[mag_z_col])
            
            mag_intensity = np.sqrt(mag_x**2 + mag_y**2 + mag_z**2)
            has_mag = True
            print("   Magnetometer loaded.")
        except:
            mag_intensity = t
            has_mag = False
            
    except Exception as e:
        print(f"   Error: {e}")
        return

    # --- PHYSICS ENGINE ---
    dt = np.mean(np.diff(t))
    fs = 1 / dt
    
    def lowpass_filter(data, cutoff, fs, order=4):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    # Filter
    CUTOFF = 2.0 # Hz
    ax_filt = lowpass_filter(ax, CUTOFF, fs)
    ay_filt = lowpass_filter(ay, CUTOFF, fs)
    
    # Detrend
    def detrend_signal(signal):
        drift = np.linspace(signal[0], signal[-1], len(signal))
        return signal - drift

    # Integrate
    vx_raw = np.cumsum(ax_filt * dt)
    vy_raw = np.cumsum(ay_filt * dt)
    
    vx_clean = detrend_signal(vx_raw)
    vy_clean = detrend_signal(vy_raw)
    
    # Velocity Threshold
    VEL_THRESHOLD = 0.02 
    vx_clean[np.abs(vx_clean) < VEL_THRESHOLD] = 0
    vy_clean[np.abs(vy_clean) < VEL_THRESHOLD] = 0
    
    # Position
    px = np.cumsum(vx_clean * dt)
    py = np.cumsum(vy_clean * dt)
    if (input("Detrend position? (y/n): ").lower() == 'y'):
        px = detrend_signal(px)
        py = detrend_signal(py)

    # --- PLOT SETUP ---
    print("2. Opening Interactive Windows...")
    
    try:
        root = tk.Tk()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
        dpi = 100
    except:
        screen_w, screen_h = 1920, 1080
        dpi = 100

    # --- WINDOW 1: MAP ---
    fig_map = plt.figure(num="Trajectory Map", figsize=(screen_w*WINDOW_1_W_PCT/dpi, screen_h*WINDOW_H_PCT/dpi), dpi=dpi)
    plt.subplots_adjust(bottom=0.15)
    ax_map = fig_map.add_subplot(111)
    
    margin = 0.1
    w = np.max(px) - np.min(px)
    h = np.max(py) - np.min(py)
    if w==0: w=1
    if h==0: h=1
    
    ax_map.set_xlim(np.min(px) - w*margin, np.max(px) + w*margin)
    ax_map.set_ylim(np.min(py) - h*margin, np.max(py) + h*margin)
    ax_map.set_aspect('equal')
    ax_map.grid(True, linestyle='--', alpha=0.5)
    ax_map.set_title("Position Heatmap (Color = Magnetic Field µT)", fontsize=14)
    ax_map.set_xlabel("X (m)")
    ax_map.set_ylabel("Y (m)")
    
    heatmap = ax_map.scatter(px, py, c=mag_intensity, cmap='plasma', s=30, alpha=0.6, label='Magnetic Field')
    point_path, = ax_map.plot([], [], marker='o', color='lime', markersize=14, markeredgecolor='black')
    
    cbar = plt.colorbar(heatmap, ax=ax_map)
    cbar.set_label('Magnetic Field (µT)')

    # --- WINDOW 2: GRAPHS ---
    fig_graphs = plt.figure(num="Physics Data", figsize=(screen_w*WINDOW_2_W_PCT/dpi, screen_h*WINDOW_H_PCT/dpi), dpi=dpi)
    plt.subplots_adjust(bottom=0.15, hspace=0.4)
    
    # 4 Subplots: Vel X, Vel Y, Acc X, Acc Y
    ax_vx = fig_graphs.add_subplot(411)
    ax_vy = fig_graphs.add_subplot(412)
    ax_ax = fig_graphs.add_subplot(413)
    ax_ay = fig_graphs.add_subplot(414)
    
    # Graph 1: Velocity X
    ax_vx.set_title("Velocity X (m/s)")
    ax_vx.grid(True, alpha=0.3)
    ax_vx.set_xlim(t[0], t[-1])
    ax_vx.set_ylim(np.min(vx_clean), np.max(vx_clean))
    line_vx, = ax_vx.plot([], [], color='orange', linewidth=2)
    point_vx, = ax_vx.plot([], [], marker='o', color='red', markersize=5)
    ax_vx.plot(t, vx_clean, color='orange', alpha=0.2) 

    # Graph 2: Velocity Y
    ax_vy.set_title("Velocity Y (m/s)")
    ax_vy.grid(True, alpha=0.3)
    ax_vy.set_xlim(t[0], t[-1])
    ax_vy.set_ylim(np.min(vy_clean), np.max(vy_clean))
    line_vy, = ax_vy.plot([], [], color='green', linewidth=2)
    point_vy, = ax_vy.plot([], [], marker='o', color='red', markersize=5)
    ax_vy.plot(t, vy_clean, color='green', alpha=0.2)

    # Graph 3: Acceleration X (Filtered)
    ax_ax.set_title("Acceleration X (m/s²)")
    ax_ax.grid(True, alpha=0.3)
    ax_ax.set_xlim(t[0], t[-1])
    ax_ax.set_ylim(np.min(ax_filt), np.max(ax_filt))
    line_ax, = ax_ax.plot([], [], color='purple', linewidth=1.5)
    point_ax, = ax_ax.plot([], [], marker='o', color='red', markersize=5)
    ax_ax.plot(t, ax_filt, color='purple', alpha=0.2)

    # Graph 4: Acceleration Y (Filtered)
    ax_ay.set_title("Acceleration Y (m/s²)")
    ax_ay.grid(True, alpha=0.3)
    ax_ay.set_xlim(t[0], t[-1])
    ax_ay.set_ylim(np.min(ay_filt), np.max(ay_filt))
    line_ay, = ax_ay.plot([], [], color='teal', linewidth=1.5)
    point_ay, = ax_ay.plot([], [], marker='o', color='red', markersize=5)
    ax_ay.plot(t, ay_filt, color='teal', alpha=0.2)
    ax_ay.set_xlabel("Time (s)")

    # --- SLIDER SETUP ---
    ax_slider = plt.axes([0.2, 0.02, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    total_frames = len(t) - 1
    
    slider = Slider(
        ax=ax_slider,
        label='Time Scrub ',
        valmin=0,
        valmax=total_frames,
        valinit=0,
        valstep=1
    )

    def update(val):
        idx = int(slider.val)
        current_t = t[:idx]
        
        # Window 1 Update
        point_path.set_data([px[idx]], [py[idx]])
        
        # Window 2 Update
        line_vx.set_data(current_t, vx_clean[:idx])
        point_vx.set_data([t[idx]], [vx_clean[idx]])
        
        line_vy.set_data(current_t, vy_clean[:idx])
        point_vy.set_data([t[idx]], [vy_clean[idx]])
        
        line_ax.set_data(current_t, ax_filt[:idx])
        point_ax.set_data([t[idx]], [ax_filt[idx]])
        
        line_ay.set_data(current_t, ay_filt[:idx])
        point_ay.set_data([t[idx]], [ay_filt[idx]])
        
        fig_map.canvas.draw_idle()
        fig_graphs.canvas.draw_idle()

    slider.on_changed(update)
    
    plt.show()

if __name__ == "__main__":
    trajectory_heatmap_slider()