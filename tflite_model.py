from tflite_model_maker import image_classifier
from tflite_model_maker.image_classifier import DataLoader

import tensorflow as tf
assert tf.__version__.startswith('2')

import matplotlib.pyplot as plt
import numpy as np
import seedir as sd

image_path = './dinosaur_photo'
sd.seedir(image_path, style='spaces', indent=4, anystart='- ')
data = DataLoader.from_folder(image_path)
train_data, test_data = data.split(0.9)

model = image_classifier.create(train_data, epochs=15, batch_size=50, shuffle=True)

loss, accuracy = model.evaluate(test_data)

model.export(export_dir='.')