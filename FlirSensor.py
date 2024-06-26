import numpy as np
from PIL import Image
import json
import os
import time
import random

# Function to map pixel values to temperatures
def map_pixel_to_temperature(pixel_values, min_temp, max_temp):
    """
    Maps pixel values to temperature values.
    Parameters:
    pixel_values (np.array): 2D array of pixel values.
    min_temp (float): Minimum temperature value.
    max_temp (float): Maximum temperature value.
    Returns:
    np.array: 2D array of temperature values.
    """
    # Normalize pixel values to range [0, 1]
    normalized_pixel_values = pixel_values / 255.0
    # Map normalized values to temperature range
    temperature_values = normalized_pixel_values * (max_temp - min_temp) + min_temp
    return temperature_values

# Function to load the bitmap image and convert it to temperature values
def load_and_convert_bitmap(file_path, min_temp, max_temp):
    """
    Loads a bitmap image and converts it to temperature values.
    Parameters:
    file_path (str): Path to the bitmap image file.
    min_temp (float): Minimum temperature value.
    max_temp (float): Maximum temperature value.
    Returns:
    np.array: 2D array of temperature values.
    """
    image = Image.open(file_path).convert('L')  # Convert to grayscale
    pixel_values = np.array(image)
    return map_pixel_to_temperature(pixel_values, min_temp, max_temp)

# Function to calculate the maximum temperature
def calculate_max_temperature(temperature_values):
    """
    Calculates the maximum temperature from the temperature data.
    Parameters:
    temperature_values (np.array): 2D array of temperature values.
    Returns:
    float: Maximum temperature.
    """
    return np.max(temperature_values)

# Function to generate a random patient ID
def generate_random_patient_id():
    """
    Generates a random patient ID consisting of 3 digits.
    Returns:
    str: Randomly generated patient ID.
    """
    return str(random.randint(1, 999))

# Function to generate a JSON filename
def generate_json_filename(patient_id):
    """
    Generates a JSON filename based on the current time and patient ID.
    Parameters:
    patient_id (str): ID of the patient.
    Returns:
    str: Generated JSON filename.
    """
    current_time = time.strftime("%d-%m--%H.%M")
    filename = f"{current_time}--{patient_id}.json"
    return filename

# Function to get the latest file from a directory
def get_latest_file(directory):
    """
    Gets the latest file from a specified directory.
    Parameters:
    directory (str): Path to the directory.
    Returns:
    str: Path to the latest file.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")
    
    files = os.listdir(directory)
    if not files:
        raise FileNotFoundError(f"No files found in the directory: {directory}")
    
    paths = [os.path.join(directory, file) for file in files]
    latest_file = max(paths, key=os.path.getctime)
    return latest_file

# Main function
def main():
    # Configuration
    ambient_temp = 20.0  # Ambient temperature in degrees Celsius
    body_temp = 37.0  # Human body temperature in degrees Celsius
    bitmap_folder_path = 'bmpOutput'  # Folder containing bitmap images
    patient_id = generate_random_patient_id()
    json_filename = generate_json_filename(patient_id)
    json_output_path = os.path.join('TempOutput', json_filename)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

    try:
        # Get the latest bitmap file
        latest_bitmap_file = get_latest_file(bitmap_folder_path)
    except FileNotFoundError as e:
        print(e)
        return

    # Load the bitmap image and convert to temperature values
    temperature_values = load_and_convert_bitmap(latest_bitmap_file, ambient_temp, body_temp)

    # Calculate the maximum temperature
    max_temperature = calculate_max_temperature(temperature_values)

    # Write the maximum temperature, patient ID, and current time to a JSON file
    with open(json_output_path, 'w') as json_file:
        json.dump({
            'max_temperature': max_temperature,
            'patient_id': patient_id,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }, json_file)

    print(f"Maximum Temperature: {max_temperature:.2f}°C")
    print(f"Temperature data saved to {json_output_path}")

if __name__ == "__main__":
    main()
