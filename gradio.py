
import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.applications.vgg16 import preprocess_input

model = load_model('custom_CNN.keras')

layer_outputs = [layer.output for layer in model.layers if isinstance(layer, Model.layers.Conv2D)]
activation_model = Model(inputs=model.input, outputs=layer_outputs)

def process_image(img):
    img_resized = img.resize((256, 256))
    img_array = np.array(img_resized) / 255.0
    img_expanded = np.expand_dims(img_array, axis=0)
    return img_expanded

def generate_prediction(img_array):
    prediction = model(img_array, training=False)
    percent = prediction.numpy()[0][0]
    return percent

def interpret_prediction(percent):
    if percent < 0.5:
        return "Positive for Pneumonia", (1 - percent) * 100
    else:
        return "Negative for Pneumonia", percent * 100

def visualize_activations(img_array):
    activations = activation_model.predict(img_array)
    first_layer_activation = activations[0][0, :, :, :]

    plt.figure(figsize=(12, 12))
    for i in range(16):
        plt.subplot(4, 4, i + 1)
        plt.imshow(first_layer_activation[:, :, i], cmap='viridis')
        plt.axis('off')

    plt.tight_layout()
    plt.savefig('layer_visualization.png')
    plt.close()
    return 'layer_visualization.png'

def predict_image(img):
    img_array = process_image(img)
    percent = generate_prediction(img_array)
    result, certainty = interpret_prediction(percent)
    certainty_str = f"{certainty:.2f}%"
    vis_path = visualize_activations(img_array)
    return f"{result} with a certainty of {certainty_str}", vis_path

gr_interface = gr.Interface(
    fn=predict_image,
    inputs=gr.Image(type="pil"),
    outputs=["text", gr.Image(type="filepath")],
    title="Pneumonia Detection",
    description="Upload a chest X-ray image to predict whether it is positive or negative for Pneumonia.",
    examples=
)

gr_interface.launch()
