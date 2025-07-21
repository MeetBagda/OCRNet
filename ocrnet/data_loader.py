import pandas as pd
import numpy as np
from glob import glob
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
from PIL import Image

plt.style.use('ggplot')


annot = pd.read_parquet('/kaggle/input/textocr-text-extraction-from-images-dataset/annot.parquet')
imgs = pd.read_parquet('/kaggle/input/textocr-text-extraction-from-images-dataset/img.parquet')
img_fns = glob('/kaggle/input/textocr-text-extraction-from-images-dataset/train_val_images/train_images/*')