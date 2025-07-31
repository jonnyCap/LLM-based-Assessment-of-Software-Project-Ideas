import os
import pandas as pd
from bs4 import BeautifulSoup
from googletrans import Translator
import re
import asyncio

INPUT_PATH = 'ICL2025-Selected-Ideas'
OUTPUT_PATH = 'preprocessed_data/icl_processed.csv'

translator = Translator()  # Initialize the translator

def extract_text_from_html(file_path):
    """Extract clean text content from an HTML file, removing extra newlines and spaces."""
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text(separator=' ')  # Replace newlines with spaces
        text = re.sub(r'\s+', ' ', text).strip()  # Remove excessive spaces/newlines
        return text

async def translate_to_english(text):
    """Translate text to English if it is not already in English."""
    if text.strip():  # Ensure text is not empty
        translated = await translator.translate(text, dest='en')
        return translated.text
    return text  # Return original if empty

async def process_folders(input_path, output_path):
    """Go through each subfolder, extract content from onlinetext.html, translate to English, and save to CSV."""
    data = []
    file_names = []
    
    for file in os.listdir(input_path):
        html_file_path = os.path.join(input_path, file)
        if file.endswith('.html') and os.path.isfile(html_file_path):
            if os.path.exists(html_file_path):
                text_content = extract_text_from_html(html_file_path)
                translated_content = await translate_to_english(text_content)  # Translate to English
                data.append(translated_content)
                file_names.append(file)
    """
    for folder in os.listdir(input_path):
        folder_path = os.path.join(input_path, folder)
        if os.path.isdir(folder_path):  # Ensure it's a directory
            html_file_path = os.path.join(folder_path, 'onlinetext.html')
            if os.path.exists(html_file_path):
                text_content = extract_text_from_html(html_file_path)
                translated_content = translate_to_english(text_content)  # Translate to English
                data.append(translated_content)
    """
    # Save extracted content to CSV using pandas
    df = pd.DataFrame({'Index': range(len(data)), 'File': file_names, 'Content': data})
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')

    print("CSV Content:")
    print(df)

    # Print result
def print_result(output_path):
    df = pd.read_csv(output_path, encoding='utf-8')
    result_dict = df.set_index('Index')['Content'].to_dict()
    print(result_dict)

if __name__ == "__main__":
    asyncio.run(process_folders(INPUT_PATH, OUTPUT_PATH))
    print(f"Processed data saved to {OUTPUT_PATH}")
    print_result(OUTPUT_PATH)

