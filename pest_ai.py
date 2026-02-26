# import tensorflow as tf
# import cv2
# import numpy as np
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODELS_DIR = os.path.join(BASE_DIR, "models")

# MODELS = {
#     "maize": tf.keras.models.load_model(
#         os.path.join(MODELS_DIR, "maize_disease_model.keras"),
#         compile=False
#     ),
#     "cotton": tf.keras.models.load_model(
#         os.path.join(MODELS_DIR, "cotton_disease_model.keras"),
#         compile=False
#     ),
#     "chickpea": tf.keras.models.load_model(
#         os.path.join(MODELS_DIR, "chickpea_disease_model.keras"),
#         compile=False
#     ),
#     "groundnut": tf.keras.models.load_model(
#         os.path.join(MODELS_DIR, "groundnut_disease_model.keras"),
#         compile=False
#     ),
#     "moong": tf.keras.models.load_model(
#         os.path.join(MODELS_DIR, "moong_disease_model.keras"),
#         compile=False
#     ),
#     "tur": tf.keras.models.load_model(
#         os.path.join(MODELS_DIR, "tur_disease_model.keras"),
#         compile=False
#     ),
# }

# # -------- MAIN DISEASE FUNCTION --------
# def predict_pest(image_path, crop):
#     """
#     Returns:
#       status  -> healthy / diseased / uncertain
#       confidence -> float (0–1)
#     """

#     # safety check
#     if crop not in MODELS:
#         return "unsupported", 0.0

#     model = MODELS[crop]

#     # read & preprocess image
#     img = cv2.imread(image_path)
#     if img is None:
#         return "uncertain", 0.0

#     img = cv2.resize(img, (224, 224))
#     img = img.astype("float32") / 255.0
#     img = np.expand_dims(img, axis=0)

#     # model prediction (sigmoid output: 0–1)
#     prob = float(model.predict(img)[0][0])

#     # -------- CORRECT INTERPRETATION --------
#     # class 1 = healthy
#     # class 0 = diseased

#     if prob >= 0.70:
#         return "healthy", prob

#     elif prob <= 0.30:
#         return "diseased", 1 - prob

#     else:
#         return "uncertain", prob

# def predict_pest(image_path, crop):
#     return "healthy", 0.95