import easyocr
from PIL import Image, UnidentifiedImageError
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import os
import numpy as np

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

def extract_text(img):
    """Performs OCR on the given PIL Image and returns recognized texts list."""
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(np.array(img))
    return [text for (_, text, _) in results]

if __name__ == "__main__":
    img_path = input('Enter image path (local, URL, or Google Drive link): ').strip()
    try:
        img = load_image(img_path)
        plt.imshow(img)
        plt.axis('off')
        plt.show()
        texts = extract_text(img)
        print('\nExtracted Text:')
        if texts:
            for t in texts:
                print(t)
        else:
            print('[No text found]')
    except Exception as e:
        print(f'\nError: {e}')
