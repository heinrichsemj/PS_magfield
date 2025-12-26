# Magnetic Field Heat Map Scanner

This project generates high-resolution magnetic field heat maps by combining **ultrasonic position tracking** (using an Arduino) with **magnetic field data** (recorded via the Phyphox smartphone app).

## Project Structure

* `process_table.py`: The main Python script that merges data and generates the heat maps.
* `ultrasoundStartStop.ino`: The Arduino firmware for the position tracking system.
* `tableX.txt`: Ultrasonic log files (Position Data).
* `tableX.csv`: Magnetic field log files (Sensor Data).

---

## Setup & Requirements

### 1. Hardware Setup (Arduino)
Upload the `ultrasoundStartStop.ino` sketch to your Arduino. Connect your sensors as defined in the code:

* **Ultrasonic Sensor 1 (S1 - Horizontal):** Trig Pin **9**, Echo Pin **10**
* **Ultrasonic Sensor 2 (S2 - Vertical):** Trig Pin **5**, Echo Pin **6**
* **Start/Stop Button:** Pin **2** (Connect between Pin 2 and GND)

**Usage:**
1. Open the **Serial Monitor** (Baud Rate: **9600**).
2. Press the button to **START** logging. The Serial Monitor will print `--- STARTED ---`.
3. Move the apparatus over the surface.
4. Press the button again to **STOP**.
5. Copy the entire output from the Serial Monitor into a text file (e.g., `table1.txt`).

### 2. Smartphone Setup (Phyphox App)
To ensure the Python script reads your magnetic data correctly, you must select the specific CSV format that uses commas as delimiters and dots for decimals.

1. Open **Phyphox** on your smartphone.
2. Select the **"Magnetometer"** experiment.
3. Start the recording, perform your scan, and stop.
4. Go to the experiment menu (three dots) -> **Export**.
5. **CRITICAL:** Select **CSV (Comma, decimal point)**.
   * *Do NOT select Semicolon or Tab formats, or the script will fail to read the headers.*
6. Transfer the file to your computer and rename it (e.g., `table1.csv`).

### 3. Python Environment
Ensure you have Python installed with the necessary data science libraries:
  pip install pandas numpy matplotlib scipy
