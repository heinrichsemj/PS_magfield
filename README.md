# P&S: Magnetic Fields in Daily Life
### Measurement of Magnetic Fields and Heatmap Generation

This repository contains the documentation, raw datasets, and custom hardware implementation for a study on localized magnetic field mapping conducted at **ETH Zurich**. The project evaluates manual, ultrasonic, and inertial methodologies to characterize the magnetic topographies of our daily environment.

## Repository Structure

* **`PS_magnet.pdf`**: The final research report documenting our findings, methodologies, and results.
* **`/Arduino`**:cContains the hardware logic and assembly for the automated tracking system.
    * `Arduino_Sensors.ino`: Script for controlling ultrasonic sensors and generating synchronized timestamps.
    * Wiring diagrams and breadboard layouts for the Arduino UNO integration.
* **`/EXPOM&Accelerometer`**: Core directory for data processing and visualization.
    * `heatmap_Tisch_Scheune_magnetisch.py`: Python script for generating 3D topologies and interpolated heatmaps.
    * `Inside_Outside.csv`: Transitional data capturing field variations between indoor and outdoor environments.
---

## Hardware Implementation (Arduino & Ultrasound)

The centerpiece of the automated tracking method is the integrated Arduino-ultrasound apparatus. This system was developed to address the temporal inefficiency of manual grid measurements by providing real-time spatial coordinates for magnetic field readings.

### System Architecture
* **Microcontroller**: Arduino UNO board acting as the central processing unit.
* **Spatial Tracking**: Two ultrasonic distance sensors mounted on a protoboard/breadboard to triangulate position relative to the table edges.
* **Magnetic Sensing**: A smartphone running the **Phyphox** application serves as the magnetometer.
* **Data Fusion Strategy**: The Arduino outputs a serial stream containing a timestamp and dual ultrasound readings. These are post-synchronized with the smartphone's magnetic field CSV export by correlating start-times.

### Operational Procedure
1. **Coupling**: The smartphone is physically coupled with the ultrasonic sensors on the breadboard to ensure the sensor frame of reference matches the magnetometer.
2. **Synchronization**: The Arduino serial monitor and Phyphox app are started simultaneously.
3. **Scanning**: The apparatus is traversed smoothly across the measurement surface (e.g., the Barn Table).
4. **Processing**: Raw distance data is filtered for outliers and processed via cubic interpolation in Python to generate continuous heatmaps.

---

## 🛠 Software Requirements & Usage

### Python Environment
To run the analysis scripts found in `/Arduino`, install the following dependencies:

```bash
pip install numpy scipy matplotlib
