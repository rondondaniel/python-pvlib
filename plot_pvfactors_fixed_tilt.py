"""
Fixed-Tilt Simulation with pvfactors
====================================

Modeling the irradiance on the rear side of a fixed-tilt array.
"""

# %%
# Because pvfactors was originally designed for modeling single-axis
# tracking systems, it's not necessarily obvious how to use it to model
# fixed-tilt systems correctly.
# This example shows how to model rear-side irradiance on a fixed-tilt
# array using :py:func:`pvlib.bifacial.pvfactors.pvfactors_timeseries`.
# .. attention::
#
#    To run this example, the ``solarfactors`` package (an implementation
#    of the pvfactors model) must be installed.  It can be installed with
#    either ``pip install solarfactors`` or ``pip install pvlib[optional]``,
#    which installs all of pvlib's optional dependencies.

import pandas as pd
import numpy as np
from pvlib import location, pvsystem, temperature
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import matplotlib.pyplot as plt
import warnings

# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# %%
# First, generate the usual modeling inputs:

times = pd.date_range('2025-06-21', '2025-06-22', freq='1T', tz='Etc/GMT+1')
loc = location.Location(latitude=44.867864801441954, longitude=0.3693021622181945, tz=times.tz)
sp = loc.get_solarposition(times)
cs = loc.get_clearsky(times)

AVERAGE_TEMPERATURE = 25

# example array geometry
pvrow_height = 1.13
pvrow_width = 1.935
surface_tilt = 32
gcr = pvrow_width / surface_tilt
axis_azimuth = 180
albedo = 0.2

# %%
# Now the trick: since pvfactors only wants to model single-axis tracking
# arrays, we have to pretend our fixed tilt array is a single-axis tracking
# array that never rotates.  In that case, the "axis of rotation" is
# along the length of the row, with ``axis_azimuth`` 90 degrees offset from the
# fixed ``surface_azimuth``.

irrad = pvfactors_timeseries(
    solar_azimuth=sp['azimuth'],
    solar_zenith=sp['apparent_zenith'],
    surface_azimuth=270,  # 180 is south-facing array
    surface_tilt=surface_tilt,
    axis_azimuth=axis_azimuth,  # 90 degrees off from surface_azimuth.  270 is ok too
    timestamps=times,
    dni=cs['dni'],
    dhi=cs['dhi'],
    gcr=gcr,
    pvrow_height=pvrow_height,
    pvrow_width=pvrow_width,
    albedo=albedo,
    n_pvrows=3,
    index_observed_pvrow=1
)

# turn into pandas DataFrame
irrad = pd.concat(irrad, axis=1)

# Create a proper 1x3 layout for all three plots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: Irradiance data
irrad[['total_inc_front', 'total_inc_back']].plot(ax=axes[0])
axes[0].set_ylabel('Irradiance [W m$^{-2}$]')
axes[0].set_title('Front and Back Side Irradiance')
axes[0].legend(['Front Side', 'Back Side'])

# Define a PV module
# Using a typical bifacial module parameters
module_params = {
    'pdc0': 500,  # STC power rating (W)
    'gamma_pdc': 0.038,  # Temperature coefficient (%/C)
    'bifaciality': 0.7,  # Typical bifaciality factor
}

# Calculate cell temperature using NOCT model
# Using total front irradiance as POA and assuming air temperature
temp_params = temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Create temperature data
temp_air = AVERAGE_TEMPERATURE + 5 * np.sin(np.pi * (times.hour + times.minute/60) / 12) 

cell_temp = temperature.sapm_cell(
    irrad['total_inc_front'], 
    temp_air,  # Using temperature approximation
    wind_speed=1.0,  # Assuming 1 m/s wind speed
    **temp_params
)

# Calculate DC power output using PVWatts model
# Front side contribution
dc_power_front = pvsystem.pvwatts_dc(
    irrad['total_inc_front'],
    cell_temp,
    module_params['pdc0'],
    module_params['gamma_pdc']
)

# Back side contribution (adjusted by bifaciality factor)
dc_power_back = pvsystem.pvwatts_dc(
    irrad['total_inc_back'] * module_params['bifaciality'],
    cell_temp,
    module_params['pdc0'],
    module_params['gamma_pdc']
) 

# Total power (front + back)
total_dc_power = dc_power_front + dc_power_back

# Create a DataFrame with the power production data
power_data = pd.DataFrame({
    'Front_DC_Power': dc_power_front,
    'Back_DC_Power': dc_power_back,
    'Total_DC_Power': total_dc_power
}, index=times)

# Calculate watt-hours (energy) per hour
# Since our data is minute-by-minute, divide by 60 to get Wh per minute, then sum by hour
energy_per_minute = power_data / 60  # Convert W to Wh per minute

# Resample to hourly sums (Wh per hour)
energy_hourly = energy_per_minute.resample('h').sum()  # Using 'h' instead of 'H' to avoid deprecation warning

# Plot 2: Power production (instantaneous watts)
power_data.plot(ax=axes[1])
axes[1].set_ylabel('DC Power [W]')
axes[1].set_title('Instantaneous Solar Panel Production\n(500W Bifacial Module)')

# Plot 3: Energy production (watt-hours per hour)
energy_hourly.plot(kind='bar', ax=axes[2])
axes[2].set_ylabel('Energy Production [Wh]')
axes[2].set_title('Hourly Energy Production')
axes[2].set_xticklabels([t.strftime('%H:%M') for t in energy_hourly.index], rotation=45)
axes[2].grid(axis='y')

# Add total daily energy production as text
daily_total_wh = energy_hourly['Total_DC_Power'].sum()
daily_total_kw = daily_total_wh / 1000  # Convert to kWh
axes[2].text(0.5, 0.9, f'Total Daily Production: {daily_total_wh:.1f} Wh ({daily_total_kw:.2f} kWh)',
             horizontalalignment='center', transform=axes[2].transAxes, 
             bbox=dict(facecolor='white', alpha=0.8))

plt.tight_layout()
plt.show()
