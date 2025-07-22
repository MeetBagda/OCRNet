import easyocr
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import os
import numpy as np
import matplotlib.pyplot as plt

def load_image(path):
    """
    Loads an image from a local path, web URL, or Google Drive share link.
    Returns a PIL Image object.
    """
    try:
        # Handle web URLs
        if path.startswith('http://') or path.startswith('https://'):
            # Handle Google Drive share link
            if 'drive.google.com' in path:
                if '/file/d/' in path:
                    file_id = path.split('/file/d/')[1].split('/')[0]
                    direct_url = f'https://drive.google.com/uc?export=download&id={file_id}'
                else:
                    raise ValueError('Unsupported Google Drive link format.')
                response = requests.get(direct_url)
            else:
                response = requests.get(path)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert('RGB')
        else:
            # Handle local file
            if not os.path.exists(path):
                raise FileNotFoundError(f'File not found: {path}')
            img = Image.open(path).convert('RGB')
        return img
    except UnidentifiedImageError:
        raise ValueError('Cannot identify image file. Please check its format (jpeg, png, etc).')
    except Exception as e:
        raise ValueError(f'Error loading image: {e}')

def extract_text(img):
    """
    Performs OCR on the given PIL Image object and returns extracted text.
    """
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(np.array(img))
    return [text for (_, text, _) in result]

# Main logic
img_path = input('Enter image path (local, URL, or Google Drive link): ')
try:
    img = load_image(img_path)
    # Display the image
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    # Extract and show text
    texts = extract_text(img)
    print('\nExtracted Text:')
    if texts:
        for t in texts:
            print(t)
    else:
        print('[No text found]')
except Exception as e:
    print(f'Error: {e}')
