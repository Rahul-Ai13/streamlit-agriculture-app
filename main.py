import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import speech_recognition as sr
from gtts import gTTS
import os
import random


sunlight_base_data = {
    "Bangalore": 6.5,
    "Mysore": 7.2,
    "Hubli": 8.0,
    "Mangalore": 6.8,
    "Tumkur": 7.0,
    "Davangere": 7.5,
    "Other": 6.0
}

# Base water requirements for different cities
water_base_data = {
    "Bangalore": 600,
    "Mysore": 700,
    "Hubli": 800,
    "Mangalore": 650,
    "Tumkur": 750,
    "Davangere": 720,
    "Other": 600
}

# Function for dynamic sunlight intensity
def get_dynamic_sunlight(city):
    base_sunlight = sunlight_base_data.get(city, sunlight_base_data["Other"])
    variation = random.uniform(-1, 1)  # Random variation between -1 and 1 hours
    return max(base_sunlight + variation, 0)  # Ensure sunlight is non-negative

# Function to calculate water requirement based on sunlight and city
def calculate_water_requirement(sunlight, city, language):
    base_water = water_base_data.get(city, water_base_data["Other"])
    adjustment_factor = 0.05  # Adjust water by 5% for each hour of sunlight difference
    sunlight_difference = sunlight - sunlight_base_data.get(city, sunlight_base_data["Other"])
    adjusted_water = base_water * (1 + adjustment_factor * sunlight_difference)

    # Create a mock dataset for ANOVA (optional, for display or calculation)
    data = {
        "City": [city] * 5 + ["OtherCity"] * 5,
        "Sunlight": [sunlight, sunlight + 2, sunlight - 2, sunlight + 1, sunlight - 1] * 2,
        "Water_Required": [base_water, base_water + 50, base_water - 50, base_water + 30, base_water - 20] * 2,
    }
    df = pd.DataFrame(data)

    # Return the adjusted water requirement and dataset
    return max(adjusted_water, 0), df  # Ensure water requirement is non-negative

# Function for text-to-speech
def speak_text(text, language_code):
    try:
        # Generate speech file using gTTS
        tts = gTTS(text=text, lang=language_code)
        filename = "output.mp3"
        tts.save(filename)
        
        # Display audio player in Streamlit
        st.audio(filename, format="audio/mp3", start_time=0)
    except Exception as e:
        st.write("Error with text-to-speech:", str(e))

# Function to recognize speech input
def get_voice_input(prompt, language_code):
    st.write(prompt)
    speak_text(prompt, language_code)
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        if language_code == "kn":
            return recognizer.recognize_google(audio, language="kn-IN")
        else:
            return recognizer.recognize_google(audio, language="en-IN")
    except sr.UnknownValueError:
        return None

# Function to provide plant information
def provide_plant_info(plant_name, city, sunlight, language):
    watering_info, df = calculate_water_requirement(sunlight, city, language)
    if language == "kn":
        sunlight_message = f"{city} ನಲ್ಲಿ ಸೂರ್ಯನ ಬೆಳಕು {sunlight:.2f} ಗಂಟೆಗಳು. ನೀವು ಆರಿಸಿದ ಬೆಳೆ {plant_name}."
        watering_message = f"ನಿಮ್ಮ ಬೆಳೆ ಬೆಳೆಯಲು {city} ನಲ್ಲಿ ಸರಾಸರಿ {watering_info:.2f} ಲೀಟರ್ ನೀರಿನ ಅಗತ್ಯವಿದೆ."
    else:
        sunlight_message = f"Sunlight in {city} is {sunlight:.2f} hours. You selected the plant {plant_name}."
        watering_message = f"In {city}, you need approximately {watering_info:.2f} liters of water for optimal growth."

    # Display and speak the sunlight message
    st.write(sunlight_message)
    speak_text(sunlight_message, language)

    # Display and speak the watering message
    st.write(watering_message)
    speak_text(watering_message, language)

# Main function
def main():
    # Set the page title and header
    st.set_page_config(page_title="Agriculture Assistance", page_icon="🌱")
    
    # Background and theme styling
    st.markdown(
        """
        <style>
        .reportview-container {
            background-image: linear-gradient(to right, rgba(0, 128, 0, 0.8), rgba(0, 51, 0, 0.8)), url('https://www.w3schools.com/w3images/forest.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        h1 {
            color: white !important;
            font-size: 3.5em;
            text-align: center;
            font-family: 'Roboto', sans-serif;
            text-shadow: 4px 4px 6px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Title
    st.title("ಕೃಷಿಕರಿಗೆ ಕೃಷಿ ಸಹಾಯ")
    
    # Language selection
    language = st.selectbox("Choose your language / ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ", ["English", "Kannada"])
    language_code = "kn" if language == "Kannada" else "en"

    # Plant selection
    plant_prompt = (
        "Please say the name of the plant you want to grow: Rice, Wheat, Ragi, Sugarcane, Banana, or Mango."
        if language == "English"
        else "ನೀವು ಬೆಳೆದ ಬಯಸುವ ಬೆಳೆ ಹೆಸರು ಹೇಳಿ: ಅಕ್ಕಿ, ಗೋಧಿ, ರಾಗಿ, ಕಬ್ಬು, ಬಾಳೆಹಣ್ಣು, ಅಥವಾ ಮಾವು."
    )
    plant_response = get_voice_input(plant_prompt, language_code)
    plant_mapping_en = ["rice", "wheat", "ragi", "sugarcane", "banana", "mango"]
    plant_mapping_kn = ["ಅಕ್ಕಿ", "ಗೋಧಿ", "ರಾಗಿ", "ಕಬ್ಬು", "ಬಾಳೆಹಣ್ಣು", "ಮಾವು"]

    plant_name = None
    if language == "English" and plant_response.lower() in plant_mapping_en:
        plant_name = plant_response.capitalize()
    elif language == "Kannada" and plant_response in plant_mapping_kn:
        plant_name = plant_response

    if not plant_name:
        error_message = "Invalid input. Please try again." if language == "English" else "ತಪ್ಪಾದ ಇನ್‌ಪುಟ್. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
        st.write(error_message)
        speak_text(error_message, language_code)
        return

    # City selection
    city_prompt = "Please say the name of the city where you are growing the plant." if language == "English" else "ನೀವು ಬೆಳೆ ಬೆಳೆದಿರುವ ನಗರದ ಹೆಸರನ್ನು ಹೇಳಿ."
    city = get_voice_input(city_prompt, language_code)

    if not city:
        error_message = "Invalid input. Please try again." if language == "English" else "ತಪ್ಪಾದ ಇನ್‌ಪುಟ್. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
        st.write(error_message)
        speak_text(error_message, language_code)
        return

    # Normalize city name and calculate sunlight
    city_normalized = city.capitalize()
    sunlight = get_dynamic_sunlight(city_normalized)

    # Provide plant info
    provide_plant_info(plant_name, city_normalized, sunlight, language_code)

if __name__ == "__main__":
    main()
