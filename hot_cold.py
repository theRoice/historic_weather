import json
import pandas as pd
import matplotlib.pyplot as plot
import numpy as np
import sys

# Prep file and set target for png
filename = "raw_weather_data.json"
output_plot_file = "hot_cold_months_plot.png"

# Define hot and cold months
# 1=Jan, 2=Feb, ... 12=Dec
HOT_MONTHS = [4, 5, 6, 7, 8, 9]  # April - Sep
COLD_MONTHS = [10, 11, 12, 1, 2, 3] # Oct - Mar
# ---------------------


# Load json
print(f"Loading {filename}...")
try:
    with open(filename, 'r') as f:
        weather_data = json.load(f)
except FileNotFoundError:
    print(f"\n--- ERROR ---")
    print(f"The file '{filename}' was not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"\n--- ERROR ---")
    print(f"The file '{filename}' contains invalid JSON.")
    sys.exit(1)
    
print("JSON loaded successfully.")

print("Converting JSON data to Pandas DataFrame...")
try:
    hourly_df = pd.DataFrame(weather_data['hourly'])
    units = weather_data['hourly_units']
except KeyError:
    print("\n--- ERROR ---")
    print("The JSON file is missing the expected 'hourly' or 'hourly_units' key.")
    sys.exit(1)

hourly_df['date'] = pd.to_datetime(hourly_df['time'])
indexed_df = hourly_df.set_index('date').drop(columns=['time'])

print("DataFrame created successfully.")

# Resample Data
print("Filtering and resampling data for hot/cold months...")

# Create two new DataFrames, one for hot, one for cold
hot_df = indexed_df[indexed_df.index.month.isin(HOT_MONTHS)]
cold_df = indexed_df[indexed_df.index.month.isin(COLD_MONTHS)]

# Resample to monthly frequency
monthly_hot_temp = hot_df['temperature_2m'].resample('MS').mean()

# Get the mean temp and depth for cold months
monthly_cold_temp = cold_df['temperature_2m'].resample('MS').mean()
monthly_cold_depth = cold_df['snow_depth'].resample('MS').mean()

# Get the sum of snowfall for cold months
monthly_cold_snowfall_sum = cold_df['snowfall'].resample('MS').sum()

print("Resampling complete.")

# Plot resampled data
print("Generating plot...")

fig, (ax1, ax2, ax3, ax4) = plot.subplots(4, 1, figsize=(15, 16), sharex=True)
fig.suptitle('Hot vs. Cold Month Weather Statistics (1990-2025)', fontsize=16, y=1.02)

# Helper function for plotting trend lines
def plot_trend(ax, series, color):
    """Calculates and plots a linear trend line on the given axes."""
    y = series.dropna()
    if len(y) < 2: 
        return None, None, None
    x = y.index.map(pd.Timestamp.toordinal)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(y.index, p(x), f"{color}--", label="Trend")
    return p, x, y

# Hot Months - Temperature
ax1.plot(monthly_hot_temp.index, monthly_hot_temp, color='red', label='Monthly Mean')
trend_details_1 = plot_trend(ax1, monthly_hot_temp, 'k')
ax1.set_title(f'Hot Months (Apr-Sep) Mean Temperature')
ax1.set_ylabel(f"Temp ({units.get('temperature_2m', '?')})")
ax1.legend()

# Cold Months - Temperature
ax2.plot(monthly_cold_temp.index, monthly_cold_temp, color='blue', label='Monthly Mean')
trend_details_2 = plot_trend(ax2, monthly_cold_temp, 'k')
ax2.set_title(f'Cold Months (Oct-Mar) Mean Temperature')
ax2.set_ylabel(f"Temp ({units.get('temperature_2m', '?')})")
ax2.legend()

# Cold Months - Snowfall
ax3.plot(monthly_cold_snowfall_sum.index, monthly_cold_snowfall_sum, color='blue', label='Monthly Sum')
trend_details_3 = plot_trend(ax3, monthly_cold_snowfall_sum, 'k')
ax3.set_title(f'Cold Months (Oct-Mar) Total Snowfall')
ax3.set_ylabel(f"Snowfall ({units.get('snowfall', '?')})")
ax3.legend()

# Cold Months - Snow Depth
ax4.plot(monthly_cold_depth.index, monthly_cold_depth, color='grey', label='Monthly Mean')
trend_details_4 = plot_trend(ax4, monthly_cold_depth, 'k')
ax4.set_title(f'Cold Months (Oct-Mar) Mean Snow Depth')
ax4.set_ylabel(f"Snow Depth ({units.get('snow_depth', '?')})")
ax4.legend()

# Save plot
ax4.set_xlabel('Date')
plot.tight_layout()
plot.savefig(output_plot_file)
print(f"\nSuccess! Plot saved as '{output_plot_file}'")

print("\n--- Trend Line Numerical Analysis ---")

def print_trend_details(title, details, unit=''):
    (p, x_ord, y_series) = details
    if p is None or x_ord is None or y_series is None:
        print(f"\n{title}: Not enough data to calculate trend.")
        return
    
    # Get the first and last date from the x-axis
    start_date = y_series.index[0].strftime('%Y-%m')
    end_date = y_series.index[-1].strftime('%Y-%m')
    
    # Get the start and end values from the trend line
    start_val = p(x_ord[0])
    end_val = p(x_ord[-1])
    total_change = end_val - start_val
    
    print(f"\n{title}:")
    print(f"  Trend Start ({start_date}): {start_val:.4f} {unit}")
    print(f"  Trend End   ({end_date}): {end_val:.4f} {unit}")
    print(f"  Total Change over ~35 years: {total_change:+.4f} {unit}")

# Print the details for each plot
print_trend_details(
    "Hot Months Mean Temperature",
    trend_details_1,
    units.get('temperature_2m', '?')
)
print_trend_details(
    "Cold Months Mean Temperature",
    trend_details_2,
    units.get('temperature_2m', '?')
)
print_trend_details(
    "Cold Months Total Snowfall",
    trend_details_3,
    units.get('snowfall', '?')
)
print_trend_details(
    "Cold Months Mean Snow Depth",
    trend_details_4,
    units.get('snow_depth', '?')
)
