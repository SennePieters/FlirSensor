import numpy as np
from PIL import Image
import os
import random
import time

def generate_random_temperature_bitmap(width, height, min_temp, max_temp, output_folder):
    """
    Generates a bitmap image with random temperature values between min_temp and max_temp.
    Parameters:
    width (int): Width of the bitmap image.
    height (int): Height of the bitmap image.
    min_temp (float): Minimum temperature value.
    max_temp (float): Maximum temperature value.
    output_folder (str): Path to the folder where the bitmap image will be saved.
    """
    # Generate a random maximum temperature for this image
    max_temperature = random.uniform(min_temp, max_temp)
    
    # Create an array of random temperature values
    temperature_values = np.random.uniform(min_temp, max_temperature, (height, width))
    
    # Normalize temperature values to range [0, 255] for grayscale image
    normalized_values = ((temperature_values - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)
    
    # Create a PIL image from the normalized values
    image = Image.fromarray(normalized_values, mode='L')
    
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate the current time and a random patient number
    current_time = time.strftime("%d-%m--%H.%M.%S")
    
    # Generate a filename with the current time and patient number
    filename = f"{current_time}.bmp"
    file_path = os.path.join(output_folder, filename)
    
    # Save the image
    image.save(file_path)
    print(f"Temperature bitmap saved to {file_path}")

def main():
    # Configuration
    width, height = 100, 100
    min_temp = 36.0  # Minimum temperature in degrees Celsius
    max_temp = 40.0  # Maximum temperature in degrees Celsius
    output_folder = '/app/SensorOutput'  # Folder to save the bitmap image

    # Generate and save the bitmap image
    generate_random_temperature_bitmap(width, height, min_temp, max_temp, output_folder)

if __name__ == "__main__":
    main()
