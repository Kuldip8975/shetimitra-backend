# import tensorflow as tf
# import cv2
# import numpy as np

# model = tf.keras.models.load_model("soil_model.h5")
# labels = ["black","red","sandy","clay","loam"]

# def predict_soil(image_path):
#     img = cv2.imread(image_path)
#     img = cv2.resize(img, (224,224))
#     img = img / 255.0
#     img = np.expand_dims(img, axis=0)

#     pred = model.predict(img)
#     idx = np.argmax(pred)
#     confidence = float(np.max(pred))

#     return labels[idx], confidence
