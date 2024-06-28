import numpy as np
from PIL import Image
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

# Function to map pixel values to temperatures
def map_pixel_to_temperature(pixel_values, min_temp, max_temp):
    normalized_pixel_values = pixel_values / 255.0
    temperature_values = normalized_pixel_values * (max_temp - min_temp) + min_temp
    return temperature_values

# Function to load the bitmap image and convert it to temperature values
def load_and_convert_bitmap(file_path, min_temp, max_temp):
    retry_count = 5
    for i in range(retry_count):
        try:
            image = Image.open(file_path).convert('L')
            break
        except PermissionError:
            time.sleep(1)
            if i == retry_count - 1:
                raise
    pixel_values = np.array(image)
    return map_pixel_to_temperature(pixel_values, min_temp, max_temp)

# Function to calculate the maximum temperature
def calculate_max_temperature(temperature_values):
    return np.max(temperature_values)

# Function to write data to InfluxDB
def write_to_influxdb(max_temperature, patient_id, current_time):
    influxdb_url = "http://influxdb:8086"
    token = "awPZYtjhw42qnoxpjux4ZVWEwfDWiBmrd3D33c6daNoJH2taRYhWWWwqwgLmb3ZlyB4pAbAWbYPMf3QGpL_-rQ=="
    org = "LIME"
    bucket = "flironesensor"

    client = InfluxDBClient(
        url=influxdb_url,
        token=token,
        org=org
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = Point("measurement")\
        .tag("patient_id", patient_id)\
        .field("max_temperature", float(max_temperature))\
        .time(current_time)
    write_api.write(bucket=bucket, org=org, record=data)

    print("Data written to InfluxDB successfully.")

# Function to process a new bitmap file
def process_new_file(file_path, patient_id):
    ambient_temp = 20.0
    body_temp = 37.0

    print(f"Processing file: {file_path}")
    temperature_values = load_and_convert_bitmap(file_path, ambient_temp, body_temp)
    max_temperature = calculate_max_temperature(temperature_values)
    current_time = datetime.utcnow().isoformat()

    print(f"Maximum Temperature: {max_temperature:.2f}°C")
    print(f"Time of measure: {current_time}")

    # Write data to InfluxDB
    write_to_influxdb(max_temperature, patient_id, current_time)

# File system event handler
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, patient_id):
        super().__init__()
        self.patient_id = patient_id

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.bmp'):
            print(f"New file detected: {event.src_path}")
            process_new_file(event.src_path, self.patient_id)

# Main function to start the file watcher
def main():
    patient_id = os.getenv('PATIENT_ID')
    if not patient_id:
        print("Error: PATIENT_ID environment variable not set.")
        return

    bitmap_folder_path = '/app/SensorOutput'
    event_handler = NewFileHandler(patient_id)
    observer = Observer()
    observer.schedule(event_handler, bitmap_folder_path, recursive=False)
    observer.start()

    print(f"Started monitoring {bitmap_folder_path} for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
