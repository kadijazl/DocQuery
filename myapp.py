from flask import Flask, request, render_template
from transformers import pipeline
import pytesseract
from PIL import Image, ImageDraw
import io
import base64
import warnings

app = Flask(__name__)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Initialize the pipeline
nlp = pipeline("document-question-answering", model="impira/layoutlm-document-qa")

@app.route("/", methods=["GET", "POST"])
def index():

    output_image_url = None
    answer_text = None
    question = None 

    if request.method == "POST":
        file = request.files['file']
        question = request.form['question']  # Store the question

        # Process the uploaded image
        image = Image.open(file.stream)

        # Perform document question answering
        result = nlp(image, question)

        if isinstance(result, list) and len(result) > 0:
            answer_text = result[0]['answer']  # Get the answer from the result
            confidence = result[0]['score']

            # Use pytesseract to get text and bounding boxes from the image
            ocr_data = pytesseract.image_to_data(image.convert("RGBA"), output_type=pytesseract.Output.DICT)
            n_boxes = len(ocr_data['text'])

            # Create a transparent overlay
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))  # Fully transparent overlay
            draw_overlay = ImageDraw.Draw(overlay)

            # Highlight the answer in the overlay
            for i in range(n_boxes):
                if answer_text.strip() in ocr_data['text'][i]:
                    (x, y, w, h) = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
                    draw_overlay.rectangle([x, y, x + w, y + h], fill=(0, 255, 0, 64))  # Green with alpha for transparency

            # Blend the overlay with the original image
            highlighted_image = Image.alpha_composite(image.convert("RGBA"), overlay)

            # Save the input image with highlighted text
            input_img_byte_arr = io.BytesIO()
            image.save(input_img_byte_arr, format='PNG')
            input_img_byte_arr.seek(0)

            # Save the highlighted image
            highlighted_img_byte_arr = io.BytesIO()
            highlighted_image.save(highlighted_img_byte_arr, format='PNG')
            highlighted_img_byte_arr.seek(0)

            output_image_url = "data:image/png;base64," + base64.b64encode(highlighted_img_byte_arr.getvalue()).decode()

    return render_template("/index.html", output_image_url=output_image_url, answer_text=answer_text, question=question)

if __name__ == "__main__":
    app.run(debug=True)