#!/usr/bin/env python3

def main():
    import requests
    import json
    import sys

    # API endpoint and parameters
    # OG end date is 2025-10-31 for full time frame
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 47,
        "longitude": -117,
        "start_date": "1990-01-01",
        "end_date": "2025-10-31",
        "hourly": ["temperature_2m", "snowfall", "snow_depth"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto"
    }

    output_filename = "raw_weather_data.json"

    print(f"Attempting to download weather data for {params['start_date']} to {params['end_date']}...")

    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=60)
    
        # Check for HTTP errors
        response.raise_for_status() 

        print("Download finished. Processing JSON...")
    
        data = response.json()
        
        # Open the file and write the JSON data
        # 'indent=4' makes the JSON file human-readable
        with open(output_filename, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Successfully saved data to {output_filename}")

    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt} (The request took too long)")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from response. The API might be down or returned invalid data.")
        print("Response text:", response.text[:200] + "...")
    except Exception as e:
        print(f"An unknown error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
