# import required modules
from flask import Flask, render_template, request, url_for, redirect, flash
from matplotlib.colors import rgb2hex
from sklearn.cluster import MiniBatchKMeans
from collections import Counter
from PIL import Image
import numpy as np
import os

# setup flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['UPLOAD_PATH'] = "static"


# home route
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "GET":

        return render_template("index.html")

    elif request.method == "POST":

        img = request.files["image_file"]

        if img.filename != "":

            img.save( os.path.join(app.config['UPLOAD_PATH'], img.filename) )

            img_object = Image.open(fp=f"static/{img.filename}", mode="r")  # open the image file
            img_array = np.array(img_object)  # and convert into a 2D array

            clt = MiniBatchKMeans(n_clusters=10)
            clt.fit(img_array.reshape(-1, 3))

            n_pixels = len(clt.labels_)
            counter = Counter(clt.labels_)  # count how many pixels per cluster

            # 2D array containing the RGB values of the 10 most occurring colors
            rgb_int = clt.cluster_centers_
            rgb_float = np.array(rgb_int / 255, dtype=float)  # convert to float 0-1

            # converting the RGB values to HEX values and storing it in a list
            hex_values = [rgb2hex(rgb_float[i, :]) for i in range(rgb_float.shape[0])]

            proportions = {}

            # calculating the proportion of occurrences of each pixel
            for i in counter:
                proportions[i] = np.round(counter[i] / n_pixels, 4)

            proportions = dict(sorted(proportions.items()))
            props_list = [value for (key, value) in proportions.items()]  # converting the dictionary into a list

            def to_dictionary(key, value):
                return dict(zip(key, value))

            color_dict = to_dictionary(props_list, hex_values)  # merge the two lists to a dictionary

            # sort the dictionary in descending order by the keys
            sorted_dict = dict(sorted(color_dict.items(), reverse=True))

            return render_template("index.html", image=img.filename, colors=sorted_dict)
        else:
            flash("You didn't select any file!")  # generate an error message when a file isn't uploaded
            return redirect(url_for("home"))


# start the flask application
if __name__ == "__main__":
    app.run(debug=True)
