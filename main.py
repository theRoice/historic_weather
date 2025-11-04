import json
import sys
import pandas as pd
import matplotlib.pyplot as plot
import numpy as np

# Prep file and set target for png
filename = "raw_weather_data.json"
output_plot_file = "plot_local_json.png"

# Load json
print(f"Loading {filename}... May take a moment for large files...")
try:
    with open(filename, 'r') as f:
        weather_data = json.load(f)

except FileNotFoundError:
    print(f"\n--- ERROR ---")
    print(f"The file '{filename}' was not found in this directory.")
    print("Make sure JSON is in the same directory as this script.")
    sys.exit(1)
    
except json.JSONDecodeError:
    print(f"\n--- ERROR ---")
    print(f"The file '{filename}' contains invalid JSON and could not be read.")
    sys.exit(1)

print("JSON loaded successfully")

print("Converting JSON data to Pandas DataFrame")

try:
    hourly_df = pd.DataFrame(weather_data['hourly'])
    units = weather_data['hourly_units']
except KeyError:
    print("\n--- Error ---")
    print("The JSON file is missing he expected 'hourly' or 'hourly_units' key.")
    print("Please recheck JSON structure")
    sys.exit(1)

# convert time column to datetime objects for resampling
hourly_df['date'] = pd.to_datetime(hourly_df['time'])

# set converted datetime objects as the index of the DataFrame
# additionally drop the time string column
indexed_df = hourly_df.set_index('date').drop(columns=['time'])

print("DataFrame created successfully. Head:")
print(indexed_df.head())

# resample data to daily frequency
print("Resampling data to daily frequency...")

# calculate daily mean for temp and snow depth
daily_mean = indexed_df[['temperature_2m', 'snow_depth']].resample('D').mean()
# calculate daily standard deviation for temp and snow depth
daily_std = indexed_df[['temperature_2m', 'snow_depth']].resample('D').std()

# calculate daily sum for snowfall
daily_snowfall_sum = indexed_df['snowfall'].resample('D').sum()

print("Resampling Complete")

# Generate plots
print("Generating plot...")

fig, (ax1, ax2, ax3) = plot.subplots(3, 1, figsize=(15, 12), sharex=True)
fig.suptitle('Daily Weather Statistics', fontsize=16, y=1.02)

# plot daily mean temp
ax1.plot(daily_mean.index, daily_mean['temperature_2m'], label='Daily Mean')
ax1.fill_between(daily_mean.index,
                 daily_mean['temperature_2m'] - daily_std['temperature_2m'],
                 daily_mean['temperature_2m'] + daily_std['temperature_2m'],
                 alpha=0.2, label='Standard Deviation')

# Trend line
y = daily_mean['temperature_2m'].dropna()
x = y.index.map(pd.Timestamp.toordinal)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
ax1.plot(y.index, p(x), "k--", label="Trend")
ax1.set_title('Daily Mean Temperature')
ax1.set_ylabel(f"Temperature ({units.get('temperature_2m', '?')})")
ax1.legend()

# Daily total Snowfall
ax2.plot(daily_snowfall_sum.index, daily_snowfall_sum, color='blue', label='Daily Sum')
# Trend line
y = daily_snowfall_sum.dropna()
x = y.index.map(pd.Timestamp.toordinal)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
ax2.plot(y.index, p(x), "k--", label="Trend")
ax2.set_title('Daily Total Snowfall')
ax2.set_ylabel(f"Snowfall ({units.get('snowfall', '?')})")
ax2.legend()

# Daily Mean Snow Depth
ax3.plot(daily_mean.index, daily_mean['snow_depth'], label='Daily Mean')
ax3.fill_between(daily_mean.index,
                 daily_mean['snow_depth'] - daily_std['snow_depth'],
                 daily_mean['snow_depth'] + daily_std['snow_depth'],
                 color='grey', alpha=0.2, label='Standard Deviation')
# Trend line
y = daily_mean['snow_depth'].dropna()
x = y.index.map(pd.Timestamp.toordinal)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
ax3.plot(y.index, p(x), "k--", label="Trend")
ax3.set_title('Daily Mean Snow Depth')
ax3.set_ylabel(f"Snow Depth ({units.get('snow_depth', '?')})")
ax3.legend()

# Save the Plot
ax3.set_xlabel('Date')
plot.tight_layout()
plot.savefig(output_plot_file)
print(f"\nSuccess! Plot saved as '{output_plot_file}'")
