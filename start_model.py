import tensorflow as tf
from tensorflow import keras
import numpy as np

model = keras.models.load_model('./model/dinosaurs.keras')
img_height = 180
img_width = 180

class_names = ['trex', 'triceratops']

def predict_image(path):
    img = tf.keras.utils.load_img(
        path,
        target_size = (img_height, img_width)
    )

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
    )

predict_image('./test4.jpg')
predict_image('./test3.jpg')
predict_image('./test5.jpg')
predict_image('./test6.jpg')
predict_image('./test7.jpg')
predict_image('./test9.jpg')