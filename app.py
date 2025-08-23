import ollama
import sys
import os
import argparse
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO

def get_gdrive_direct_url(url):
    """Converts a Google Drive share link to a direct download link."""
    if 'drive.google.com' in url and '/file/d/' in url:
        file_id = url.split('/file/d/')[1].split('/')[0]
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    raise ValueError('Unsupported Google Drive link format.')

def load_image(path):
    """Loads an image from a local path, URL, or Google Drive share link."""
    try:
        if path.startswith('http://') or path.startswith('https://'):
            if 'drive.google.com' in path:
                path = get_gdrive_direct_url(path)
            response = requests.get(path)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert('RGB')
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f'File not found: {path}')
            img = Image.open(path).convert('RGB')
        # Ensure image dimensions are reasonable
        if img.size[0] < 10 or img.size[1] < 10:
            raise ValueError('Image appears empty or corrupted.')
        return img
    except UnidentifiedImageError:
        raise ValueError('Cannot identify image file. Ensure it is a valid image (e.g., JPEG, PNG).')
    except Exception as e:
        raise ValueError(f'Error loading image: {e}')

def extract_text_from_image(image_path):
    """
    Extract text from an image using ollama's vision model.
    
    Args:
        image_path (str): Path to image file, URL, or Google Drive link
    
    Returns:
        str: Extracted text from the image
    """
    try:
        # Load image from path, URL, or Google Drive link
        img = load_image(image_path)
        
        # Save the image temporarily if it's from URL
        if image_path.startswith('http'):
            temp_path = 'temp_image.jpg'
            img.save(temp_path)
            image_path = temp_path
        
        # Process with ollama
        response = ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': 'extract the all text and characters from this image?',
                'images': [image_path]  
            }]
        )
        
        # Clean up temp file if created
        if image_path == 'temp_image.jpg' and os.path.exists('temp_image.jpg'):
            os.remove('temp_image.jpg')
            
        return response['message']['content']
    
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='OCR Text Extraction Tool')
    parser.add_argument('--image', '-i', help='Path to image file, URL, or Google Drive link')
    args = parser.parse_args()
    
    # If no arguments provided, prompt user for input
    if args.image:
        image_path = args.image
    else:
        image_path = input("Enter image path, URL, or Google Drive link: ").strip()
    
    result = extract_text_from_image(image_path)
    print("\nExtracted Text:")
    print(result)

if __name__ == "__main__":
    main()
