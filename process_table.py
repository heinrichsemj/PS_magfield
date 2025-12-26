import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime, timedelta
from scipy.interpolate import griddata, interp1d
from scipy.signal import medfilt

# --- Configuration ---
FILTER_S1_THRESHOLD = 53  # cm

# --- File Mapping ---
DATASETS = {
    '1': ('table1.txt', 'table1.csv', 'Table 1'),
    '2': ('table2.txt', 'table2.csv', 'Table 2'),
    '3': ('table3.txt', 'table3.csv', 'Table 3 (Standard)'),
    '4': ('30s_table3.txt', '30s_table3.csv', 'Table 3 (30s Scan)'),
    '5': ('10s_table3.txt', '10s_table3.csv', 'Table 3 (10s Scan)')
}

def parse_ultrasonic_robust(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    parsed_lines = []
    # Robust regex: handles floats, integers, jammed numbers, and ignores '/'
    number_pattern = r"[-+]?\d+\.\d{2}|[-+]?\d+"
    
    for line in lines:
        if '->' not in line: continue
        parts = line.split('->')
        time_str = parts[0].strip()
        content = parts[1].strip()
        
        if "STARTED" in content:
            content = content.replace("--- STARTED ---", "").strip()
            
        try:
            ts = datetime.strptime(time_str, "%H:%M:%S.%f")
        except ValueError: continue
            
        numbers = re.findall(number_pattern, content)
        vals = [float(n) for n in numbers]
        
        if not vals: continue

        points = []
        # Auto-detect format (Triplets vs Pairs)
        if len(vals) % 3 == 0:
            for i in range(0, len(vals), 3):
                points.append((vals[i+1], vals[i+2]))
        elif len(vals) % 2 == 0:
            for i in range(0, len(vals), 2):
                points.append((vals[i], vals[i+1]))
        
        if points:
            parsed_lines.append({'time': ts, 'points': points})
            
    # Interpolate Timestamps
    flat_data = []
    if not parsed_lines: return pd.DataFrame()
    
    start_time = parsed_lines[0]['time'] 
    
    for i in range(len(parsed_lines)):
        current = parsed_lines[i]
        points = current['points']
        n_points = len(points)
        
        if i < len(parsed_lines) - 1:
            duration = (parsed_lines[i+1]['time'] - current['time']).total_seconds()
            if duration < 0: duration += 86400
        else:
            duration = 0.5 
            
        step_time = duration / max(1, n_points)
        
        for j, (s1, s2) in enumerate(points):
            pt_time = current['time'] + timedelta(seconds=j*step_time)
            rel_time = (pt_time - start_time).total_seconds()
            flat_data.append({'Time_s': rel_time, 'S1': s1, 'S2': s2})
            
    return pd.DataFrame(flat_data)

def process_table_measurement(selection):
    if selection not in DATASETS:
        print("Invalid selection.")
        return
        
    pos_file, mag_file, display_name = DATASETS[selection]
    print(f"\n--- Processing {display_name} ---")
    
    try:
        pos_df = parse_ultrasonic_robust(pos_file)
        mag_df = pd.read_csv(mag_file)
    except FileNotFoundError:
        print(f"Error: Could not find {pos_file} or {mag_file}.")
        return

    # Clean Mag Header
    mag_df.columns = [c.split('(')[0].strip() for c in mag_df.columns]
    mag_df.rename(columns={'Time': 'Time_s', 'Absolute field': 'B_abs'}, inplace=True)
    
    # 1. Clean Position Data
    # Fix S1=0 (Sensor Dropout)
    pos_df['S1'] = pos_df['S1'].replace(0, np.nan)
    pos_df['S1'] = pos_df['S1'].interpolate(method='linear', limit_direction='both')

    # Remove Jumps
    def clean_jumps(series, threshold=25):
        diff = series.diff().abs()
        series[diff > threshold] = np.nan
        return series.interpolate(method='linear', limit_direction='both')

    pos_df['S1'] = clean_jumps(pos_df['S1'])
    pos_df['S2'] = clean_jumps(pos_df['S2'])

    # 2. ADAPTIVE SMOOTHING BASED ON DATA DENSITY
    n_points = len(pos_df)
    if n_points > 500:
        # Standard smoothing for dense data
        pos_df['S1'] = medfilt(pos_df['S1'], kernel_size=7)
        pos_df['S2'] = medfilt(pos_df['S2'], kernel_size=7)
        pos_df['S1'] = pos_df['S1'].rolling(window=5, center=True, min_periods=1).mean()
        pos_df['S2'] = pos_df['S2'].rolling(window=5, center=True, min_periods=1).mean()
    else:
        # Minimal smoothing for sparse/fast scans to preserve shape
        print(f"Notice: Sparse data detected ({n_points} points). Reducing smoothing.")
        pos_df['S1'] = medfilt(pos_df['S1'], kernel_size=3)
        pos_df['S2'] = medfilt(pos_df['S2'], kernel_size=3)

    # 3. Synchronize
    f_s1 = interp1d(pos_df['Time_s'], pos_df['S1'], kind='linear', bounds_error=False, fill_value=np.nan)
    f_s2 = interp1d(pos_df['Time_s'], pos_df['S2'], kind='linear', bounds_error=False, fill_value=np.nan)

    mag_df['S1'] = f_s1(mag_df['Time_s'])
    mag_df['S2'] = f_s2(mag_df['Time_s'])
    merged_df = mag_df.dropna(subset=['S1', 'S2'])

    # 4. Filter Artifacts
    clean_df = merged_df[merged_df['S1'] > FILTER_S1_THRESHOLD].copy()
    print(f"Generated {len(clean_df)} valid points.")

    # 5. Plot
    x = clean_df['S1']
    y = clean_df['S2']
    z = clean_df['B_abs']

    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.linspace(y.min(), y.max(), 300)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((x, y), z, (xi, yi), method='linear')

    plt.figure(figsize=(10, 8))
    plt.pcolormesh(xi, yi, zi, cmap='inferno', shading='auto')
    
    cbar = plt.colorbar()
    cbar.set_label('Magnetic Field Strength (µT)', fontsize=12)
    plt.title(f'Magnetic Heat Map - {display_name}', fontsize=14)
    plt.xlabel('Position S1 (cm)', fontsize=12)
    plt.ylabel('Position S2 (cm)', fontsize=12)
    plt.axis('equal')
    
    # Rotate 180°
    plt.gca().invert_xaxis()
    plt.gca().invert_yaxis()

    # Save Prompt
    save = input("Do you want to save this map? (y/n): ").strip().lower()
    if save in ['y', 'yes']:
        fname = display_name.replace(" ", "_").replace("(", "").replace(")", "").lower() + ".png"
        plt.savefig(fname)
        print(f"Saved as {fname}")
    
    plt.show()

# --- Main ---
if __name__ == "__main__":
    print("Unified Magnetic Table Scanner")
    for key, val in DATASETS.items():
        print(f"{key}: {val[2]}")
    
    sel = input("\nSelect measurement (1-5): ")
    process_table_measurement(sel)