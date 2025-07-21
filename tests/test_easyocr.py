import easyocr
import matplotlib.pyplot as plt
import os
from glob import glob

# Set up EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Path to images (update if needed)
image_dir = os.path.join('..', 'dataset', 'ocr_dataset', 'train_val_images', 'train_images')
print(f"{image_dir}")
image_paths = glob(os.path.join(image_dir, '*.jpg'))

# Select 3 to 5 images for testing
test_images = image_paths[:5]

for idx, img_path in enumerate(test_images):
    print(f'\nTesting image {idx+1}: {img_path}')
    results = reader.readtext(img_path)
    for bbox, text, conf in results:
        print(f'Text: {text}, Confidence: {conf:.2f}')
    # Optionally display image with annotations
    img = plt.imread(img_path)
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.title(f'OCR Results for Image {idx+1}')
    plt.axis('off')
    plt.show()
