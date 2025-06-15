# Python PVLib Solar Panel Production Modeling

A Python project for modeling solar panel production using the pvlib library. This tool calculates and visualizes the relationship between solar irradiance and actual power production for bifacial solar panels.

## Features

- Models irradiance on both front and back sides of a bifacial solar panel
- Calculates instantaneous power production in watts
- Provides hourly energy production in watt-hours
- Summarizes total daily production in kWh
- Visualizes all results in an easy-to-understand format

## Requirements

- Python 3.8+
- pvlib
- pandas
- numpy
- matplotlib
- solarfactors (for bifacial modeling)

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:danielrondon/python-pvlib.git
   cd python-pvlib
   ```

2. Set up a conda environment with the necessary dependencies:
   ```bash
   conda create -n pvlib python=3.8
   conda activate pvlib
   pip install pvlib pandas matplotlib numpy
   pip install solarfactors  # For bifacial modeling
   ```

## Usage

Run the main script to generate solar production estimates:

```bash
python plot_pvfactors_fixed_tilt.py
```

You can modify the script parameters to match your specific solar panel setup:
- Panel dimensions
- Surface tilt and azimuth
- Panel wattage and bifaciality factor
- Location (latitude/longitude)

## How It Works

The script models solar panel production in several steps:
1. Calculates clear sky irradiance for a specific location and date
2. Models irradiance on front and back of the panel using pvfactors
3. Estimates cell temperature based on irradiance and ambient conditions
4. Calculates DC power output using the PVWatts model
5. Aggregates minute-level data into hourly energy production
6. Visualizes results in a 3-panel plot showing irradiance, power, and energy

## Configuration

Key parameters can be adjusted in the script:
- `times`: Date range for simulation
- `loc`: Location coordinates (latitude/longitude)
- `surface_tilt`: Tilt angle of the solar array
- `surface_azimuth`: Direction the array faces (270° is west)
- `module_params`: Solar panel specifications

## Developer

- Daniel Rondon

## License

This project is licensed under the MIT License - see the LICENSE file for details.
