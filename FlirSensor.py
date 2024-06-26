import numpy as np
from PIL import Image
import json
import os
import time
import random

# Function to generate a bitmap image of a human body
def generate_human_body_bitmap(width, height, body_temp, ambient_temp, file_path):
    """
    Generates a bitmap image simulating a human body with a specific temperature in an ambient environment.
    Parameters:
    width (int): Width of the bitmap image.
    height (int): Height of the bitmap image.
    body_temp (float): Temperature of the human body.
    ambient_temp (float): Ambient temperature.
    file_path (str): Path to save the bitmap image.
    """
    # Create an empty 2D array for temperature values
    temperature_values = np.full((height, width), ambient_temp)
    
    # Define the human body region (a simple oval in the center)
    for y in range(height):
        for x in range(width):
            if ((x - width // 2) ** 2) / (width // 4) ** 2 + ((y - height // 2) ** 2) / (height // 2) ** 2 <= 1:
                temperature_values[y, x] = body_temp
    
    # Normalize temperature values to range [0, 255] for grayscale image
    min_temp = min(body_temp, ambient_temp)
    max_temp = max(body_temp, ambient_temp)
    normalized_values = ((temperature_values - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)
    
    # Create a PIL image from the normalized values
    image = Image.fromarray(normalized_values, mode='L')
    image.save(file_path)

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
    return str(random.randint(100, 999))

# Function to generate a JSON filename
def generate_json_filename(patient_id):
    """
    Generates a JSON filename based on the current time and patient ID.
    Parameters:
    patient_id (str): ID of the patient.
    Returns:
    str: Generated JSON filename.
    """
    current_time = time.strftime("%d%m-%H.%M")
    filename = f"{current_time}-{patient_id}.json"
    return filename

# Main function
def main():
    # Configuration
    width, height = 100, 100
    body_temp = 37.0  # Human body temperature in degrees Celsius
    ambient_temp = 20.0  # Ambient temperature in degrees Celsius
    bitmap_file_path = 'bmpOutput/thermal_image.bmp'
    patient_id = generate_random_patient_id()
    json_filename = generate_json_filename(patient_id)
    json_output_path = os.path.join('TempOutput', json_filename)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

    # Generate and save the bitmap image
    generate_human_body_bitmap(width, height, body_temp, ambient_temp, bitmap_file_path)

    # Load the bitmap image and convert to temperature values
    temperature_values = load_and_convert_bitmap(bitmap_file_path, ambient_temp, body_temp)

    # Calculate the maximum temperature
    max_temperature = calculate_max_temperature(temperature_values)

    # Write the maximum temperature to a JSON file
    with open(json_output_path, 'w') as json_file:
        json.dump({'max_temperature': max_temperature}, json_file)

    print(f"Maximum Temperature: {max_temperature:.2f}°C")
    print(f"Temperature data saved to {json_output_path}")

if __name__ == "__main__":
    main()
