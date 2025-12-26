# Magnetic Field Analysis: Processing Scripts & Raw Data

This directory contains the Python-based signal processing logic and raw sensor datasets used for the **ETH Zurich** project on localized magnetic field characterization. These tools facilitate the transition from discrete sensor readings to continuous surface visualizations and 3D topologies.

## File Manifest

### Analysis Scripts
* **`heatmap_Tisch_Scheune_magnetisch.py`**: The primary processing script for the "Table in Barn" (Scheune) experiments. It implements cubic interpolation to visualize local dipole effects and structural asymmetries.

### Raw Datasets
* **`Inside_Outside.csv`**: Time-series data capturing the magnetic flux density ($B$) transition between residential indoor spaces and outdoor environments. This dataset illustrates field attenuation caused by reinforced concrete and electrical cabling in walls.
* **`Export_ELF_x.csv`**: Baseline ground-truth data recorded using the high-precision **Expom-Elf Magnetometer**. Measurements were captured on a x cm grid across a house ground floor.
* **Supporting Band Files (LF, MF, HF, High-B)**: Segmented magnetometer data used to analyze specific frequency bands and identify localized perturbations.

---

## Setup & Usage

To execute the visualization scripts, ensure the following Python dependencies are installed:

```bash
pip install numpy scipy matplotlib
