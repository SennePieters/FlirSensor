import numpy as np
from PIL import Image
import json
import os
import time
import random
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

# Function to generate a random patient ID
def generate_random_patient_id():
    return str(random.randint(1, 999))

# Function to generate a JSON filename
def generate_json_filename(patient_id):
    current_time = time.strftime("%d-%m--%H.%M")
    filename = f"{current_time}--{patient_id}.json"
    return filename

# Function to check if a file has already been processed
def is_file_processed(file_path, log_file_path):
    if not os.path.exists(log_file_path):
        return False
    with open(log_file_path, 'r') as log_file:
        processed_files = log_file.read().splitlines()
    return file_path in processed_files

# Function to log a processed file
def log_processed_file(file_path, log_file_path):
    with open(log_file_path, 'a') as log_file:
        log_file.write(file_path + '\n')

# Function to process a new bitmap file
def process_new_file(file_path):
    ambient_temp = 20.0
    body_temp = 37.0
    log_file_path = 'Log/processed_files.log'
    patient_id = generate_random_patient_id()
    json_filename = generate_json_filename(patient_id)
    json_output_path = os.path.join('TempOutput', json_filename)

    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

    if is_file_processed(file_path, log_file_path):
        print(f"The file {file_path} has already been processed.")
        return

    temperature_values = load_and_convert_bitmap(file_path, ambient_temp, body_temp)
    max_temperature = calculate_max_temperature(temperature_values)

    with open(json_output_path, 'w') as json_file:
        json.dump({
            'max_temperature': max_temperature,
            'patient_id': patient_id,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }, json_file)

    print(f"Maximum Temperature: {max_temperature:.2f}°C")
    print(f"Temperature data saved to {json_output_path}")

    log_processed_file(file_path, log_file_path)

# File system event handler
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.bmp'):
            process_new_file(event.src_path)

# Main function to start the file watcher
def main():
    bitmap_folder_path = 'SensorOutput'
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, bitmap_folder_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
