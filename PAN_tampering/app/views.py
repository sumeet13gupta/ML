from turtle import up
import turtle
from pyparsing import original_text_for
from app import app
from flask import request, render_template
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
from PIL import Image

## to add path to config
app.config['INITIAL_FILE_UPLOADS'] = 'app/static/uploads'
app.config['EXISTING_FILE'] = 'app/static/original'
app.config['GENERATED_FILE'] = 'app/static/generated'

# Route to home page 
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        #get uploaded image
        file_upload = request.files['file_upload']
        filename = file_upload.filename

        #resize and save the uploaded images
        uploaded_image = Image.open(file_upload).resize((250,160))
        uploaded_image.save(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg'))

        # resize and save the original image so that both uploaded and original are same in soize 
        original_image = Image.open(os.path.join(app.config['EXISTING_FILE'], 'image.jpg')).resize((250,160))
        original_image.save(os.path.join(app.config['EXISTING_FILE'], 'image.jpg'))

        #read uploaded and original image as array
        original_image = cv2.imread(os.path.join(app.config['EXISTING_FILE'], 'image.jpg'))
        uploaded_image = cv2.imread(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg'))

        #convert image into grayscale
        original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        uploaded_gray = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)
        
        #calculate structural similarity
        (score, diff) = structural_similarity(original_gray, uploaded_gray, full=True)
        diff = (diff*255).astype('uint8')


        # calculate thereshold and contours
        threshold = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        for c in contours:
            # applying contours on Image 
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(original_image, (x, y), (x + w, y + h), (0,0,255), 2)
            cv2.rectangle(uploaded_image, (x, y), (x + w, y + h), (0,0,255), 2)

        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_original.jpg'), original_image)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_uploaded.jpg'), uploaded_image)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_diff.jpg'), diff)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_thresh.jpg'), threshold)
        return render_template('index.html', pred=str(round(score*100,2))+'%'+ ' correct')

# Main function
if __name__ == '__main__':
    app.run(debug=True)