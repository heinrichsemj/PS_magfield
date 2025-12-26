
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import integrate, signal, interpolate
#import matplotlib.colors as colors


REAL_DISTANCE_Y = 1.60      # Länge der Linien-Messung (Tischlänge, entlang welcher gemessen wird)
TARGET_POINTS = 150      # Punkte pro Bahn

MESSUNGEN = [
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_1.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_1.csv', 
        'start_x': 0.00 
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_2.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_2.csv', 
        'start_x': 0.08
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_3.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_3.csv', 
        'start_x': 0.16  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_4.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_4.csv', 
        'start_x': 0.24  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_5.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_5.csv', 
        'start_x': 0.32  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_6.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_6.csv', 
        'start_x': 0.40  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_7.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_7.csv', 
        'start_x': 0.48  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_8.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_8.csv', 
        'start_x': 0.56  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_9.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_9.csv', 
        'start_x': 0.64  
    },
    {
        'acc_file': 'Tisch_Scheune_magnetisch/Accelerometer_Tisch_magnetisch_10.csv', 
        'mag_file': 'Tisch_Scheune_magnetisch/Magnetometer_Tisch_magnetisch_10.csv', 
        'start_x': 0.72  
    },
   
]

def lade_csv_raw(pfad, typ='acc'):
    try:
        df = pd.read_csv(pfad) 
        if typ == 'acc':
            df = df.iloc[:, :4]
            df.columns = ['Time', 'ax', 'ay', 'az']
        else: 
            df = df.iloc[:, :4]
            df.columns = ['Time', 'mx', 'my', 'mz']
        
        df['Time'] = df['Time'].astype(float)
        df = df.sort_values('Time')
        return df
    except Exception as e:
        print(f"Fehler bei {pfad}: {e}")
        return None

def resample_to_fixed_length(df, num_points):
    """
    Nimmt eine Bahn beliebiger Länge und interpoliert sie auf exakt 'num_points'.
    """
    if len(df) < 2: return df 

    
    old_indices = np.arange(len(df))
    new_indices = np.linspace(0, len(df) - 1, num_points)
    df_new = pd.DataFrame()

   
    for col in ['global_x', 'global_y', 'Magnet_Betrag']:
        if col in df.columns:
            f = interpolate.interp1d(old_indices, df[col], kind='linear')
            df_new[col] = f(new_indices)

    return df_new


def berechne_pfad_y_forced(df_acc):
    dt = df_acc['Time'].diff().mean()
    if pd.isna(dt) or dt == 0: dt = 0.002
    
    df_acc['pos_x'] = 0.0 # Keine X-Bewegung
    
    
    vy = integrate.cumulative_trapezoid(df_acc['ay'], dx=dt, initial=0)
    vy = signal.detrend(vy, type='linear')
    py_raw = integrate.cumulative_trapezoid(vy, dx=dt, initial=0)
    
   
    if abs(py_raw[-1]) > 0.01:
        scale_factor = REAL_DISTANCE_Y / py_raw[-1]
        py_corrected = py_raw * scale_factor
        if py_corrected[-1] < 0: py_corrected *= -1
        df_acc['pos_y'] = py_corrected
    else:
        df_acc['pos_y'] = np.linspace(0, REAL_DISTANCE_Y, len(df_acc))
    
    return df_acc

def main():
    magnet_matrix_list = []
    x_positions = []

    print(f"Verarbeite Bahnen (Ziel: {TARGET_POINTS} Punkte auf {REAL_DISTANCE_Y}m)...")

    for i, bahn in enumerate(MESSUNGEN):
        df_acc = lade_csv_raw(bahn['acc_file'], typ='acc')
        df_mag = lade_csv_raw(bahn['mag_file'], typ='mag')
        
        if df_acc is not None and df_mag is not None:
            df_acc = berechne_pfad_y_forced(df_acc)
            df_mag['Magnet_Betrag'] = np.sqrt(df_mag['mx']**2 + df_mag['my']**2 + df_mag['mz']**2)
            
            df_final = pd.merge_asof(
                df_mag, df_acc[['Time', 'pos_x', 'pos_y']], 
                on='Time', direction='nearest', tolerance=0.1
            ).dropna(subset=['pos_y'])

            if not df_final.empty:
                df_final['global_x'] = bahn['start_x']
                df_final['global_y'] = df_final['pos_y']

                df_resampled = resample_to_fixed_length(df_final, TARGET_POINTS)
                magnet_matrix_list.append(df_resampled['Magnet_Betrag'].values)
                x_positions.append(bahn['start_x'])
                
                print(f" -> Bahn {i+1}: {len(df_final)} -> {len(df_resampled)} Punkte resampled.")
            else:
                print(f" -> Bahn {i+1}: Leer.")

    if not magnet_matrix_list:
        print("Keine Daten.")
        return

    
    def zweiD():

        def on_key(event):
            if event.key == ' ':
                plt.close(fig)

        heatmap_data = np.array(magnet_matrix_list) 
        
        fig = plt.figure(figsize=(8, 6))
        
        ax = sns.heatmap(
            heatmap_data,
            cmap='inferno',
            cbar_kws={'label': 'Magnetfeld (µT)'},
            xticklabels=False,
            yticklabels=False
        )
        
        xticks = np.linspace(0, TARGET_POINTS, 6)
        xlabels = np.linspace(0, REAL_DISTANCE_Y, 6)
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{x:.2f}m" for x in xlabels])
        
        ax.set_yticks(np.arange(len(x_positions)) + 0.5)
        ax.set_yticklabels([f"{y:.2f}m" for y in x_positions], rotation=0) 

        plt.title(f"Magnetfeld ({TARGET_POINTS} Punkte pro Bahn)")
        
        plt.xlabel("Y-Position (Länge)")
        plt.ylabel("X-Position (Bahn)")
        
        fig.canvas.mpl_connect('key_press_event', on_key)
        plt.tight_layout()
        
        plt.gca().invert_yaxis() 
        
        plt.show()


    def dreiD():
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm

        def on_key(event):
            if event.key == ' ':
                plt.close(fig)

        Z = np.array(magnet_matrix_list) 
        x_vals = np.array(x_positions)
        y_vals = np.linspace(0, REAL_DISTANCE_Y, TARGET_POINTS)

        X, Y = np.meshgrid(x_vals, y_vals, indexing='ij')

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        surf = ax.plot_surface(
            X, Y, Z,         
            cmap='inferno',     
            linewidth=0,      
            antialiased=True,  
            rstride=1, cstride=1, 
            
        )

        ax.set_title(f"3D Magnetfeld-Topologie ({REAL_DISTANCE_Y}m)")
        ax.set_xlabel('X: Bahn-Position (m)')
        ax.set_ylabel('Y: Scan-Länge (m)')
        ax.set_zlabel('Magnetfeld (µT)')

        ax.view_init(elev=30, azim=-135) 

        fig.colorbar(surf, shrink=0.5, aspect=10, label='Magnetfeld (µT)')

        fig.canvas.mpl_connect('key_press_event', on_key)
        plt.tight_layout()
        plt.gca().invert_yaxis()  
        plt.show()

    if (input("2 D? (y/n): ").lower() == 'y'):
            zweiD()

    if (input("3 D? (y/n): ").lower() == 'y'):
            dreiD()

if __name__ == "__main__":
        main()



    