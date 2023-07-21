# import requirements needed
from flask import Flask, render_template, request, send_from_directory, url_for, Response, redirect
import os
from werkzeug.utils import secure_filename
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import ast

#from PIL import Image
from gradio_client import Client

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

PREDICT_URL = "https://guy2-guy2-airportsec-150epoch.hf.space/api/predict"
#PREDICT_URL = "https://diego7167-asl-caption.hf.space/api/predict"


def allowed_file(filename):
  return '.' in filename and filename.rsplit(
    '.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def process_image_route():

# 	# Process the image and get the dynamically generated name
# 	#heres the route f"./static/annotated/{filename}.jpeg"
# 	# thanks

# 	# Pass the image name to the results.html template
# 	return render_template('results.html',
# 	                       image_name=f'./static/annotated/{filename}')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    if 'file1' not in request.files:
      return 'There is no file1 in the form!'
    file1 = request.files['file1']

    if file1 and allowed_file(file1.filename):
      filename = secure_filename(file1.filename)
      filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file1.save(filepath)

      # Create an image URL to send to HF Space
      image_url = "https://final-project-2023-summer-computer-vision-1.2023-summer-computer-vision.repl.co/static/uploads/" + filename
      print(f"Image_url:{image_url}")

      # Send image URL to HF Space --> returns json
      client = Client("https://guy2-guy2-airportsec-150epoch.hf.space/")
      result = client.predict(
        image_url,  # str in 'url' Textbox component
        api_name="/predict")
      result = ast.literal_eval(result)
      print(f"result:{result}")
      label2color = {
        "dangerous-items": 'r',
        "Gun": 'b',
        "Knife": 'g',
        "Pliers": 'c',
        "Scissors": 'm',
        "Wrench": 'y'
      }

      img = Image.open(filepath)

      fig, ax = plt.subplots()
      ax.imshow(img)
      for idx, detection in enumerate(result[1]):
        print(detection)

        x = detection[0][0]
        y = detection[0][1]
        w = detection[0][2] - x
        h = detection[0][3] - y

        rect = patches.Rectangle(
          (x, y),
          w,
          h,
          linewidth=1,
          edgecolor=label2color[detection[2]],
          facecolor='none',
          label=detection[2] + " - Confidence: " + str(detection[1]))
        ax.add_patch(rect)

      ax.legend()
      ax.axis('off')
      plt.savefig(f"./static/annotated/{filename}")
      os.remove(f"./static/uploads/{filename}")
      print("done!")
      # process_image_route()
      return redirect(url_for('render_results', filename=filename))
      #return render_template('results.html',
                             #image_name=f'/annotated/{filename}')
      # processed_image_path = os.path.join("annotated", f"{filename}.jpeg")
      # return render_template('results.html', image_name=processed_image_path)
    else:
      return 'Invalid file type. Only allowed file types are: png, jpg, jpeg'
  """
  Inference code --> image with labels drawn
  save image to some folder with slightly diff name (labeled_img)
  Send labeled_img to results.html
  """

  return render_template('index.html')
  #return render_template('results.html', filename = slightlydiffname)

@app.route('/uploads/<filename>')
def render_results(filename):
  return render_template('results.html', image_name = f'/annotated/{filename}')
 
@app.route('/uploads/<path:filename>')
def files(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'],
                             filename,
                             as_attachment=True)


if __name__ == '__main__':
  # IMPORTANT: change url to the site where you are editing this file.
  website_url = 'url'
  port = 80
  print(f'Try to open\n\n    https://{website_url}:{port}\n\n')
  app.run(host='0.0.0.0', port=port, debug=True)
