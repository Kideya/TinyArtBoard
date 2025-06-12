from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, send_file
import glob, os

# Ratio of Pixels witdh , height
size = 10, 10
# The Array which is storing the R,G,B Values
led_array = []
# Filepath for the output
output_folder = "Arduino/TinyArtBoard"
# The Name for HTML
name = "TinyArtBoard"

app = Flask(__name__, template_folder="./static/HTML")

def save_uploaded_file():
    f = request.files["file"]
    f.save("./uploads/upload.jpg")
    return f

def crop_range(width, height):
    """
        Returns a square crop frame for the image based on the shorter image dimension.
        This centers and crops the image around its middle area.
    """
    middle_x = width / 2
    middle_y = height / 2

    if width > height:
        left = middle_x - (height / 2)
        top = 0
        right = middle_x + (height / 2)
        bottom = height
    else:
        left = 0
        top = middle_y - (width / 2)
        right = width
        bottom = middle_y + (width / 2)

    return left, top, right, bottom


def naming_images(image, sourceWidth, sourceHeight, file):
    image.save(file + f"(_pixelated) {size}.jpg")
    print("Image has been pixelated")


def checking_rgb_values(image, imageSize):
    width, height = imageSize
    for row in range(width):
        for col in range(height):
            r, g, b = image.getpixel((col, row))
            led_array.extend([r, g, b])


def saving_rgb_as_dot_h(led_array, file):
    if len(led_array) % 3 != 0:
        raise ValueError(
            "Length of Array is missing values (Needs to have an RGB Value for each LED)"
        )

    os.makedirs(
        output_folder, exist_ok=True
    )  # Ordner automatisch erstellen, falls nicht vorhanden
    file_path = os.path.join(output_folder, "led_colors.h")
    try:
        with open(file_path, "w") as f:
            f.write(f"//Generated from Image: {file} \n")
            f.write("#include <FastLED.h>\n\n")
            f.write(f"#define NUM_LEDS {len(led_array)//3}\n\n")
            f.write(f"const CRGB ledColors[NUM_LEDS] = {{\n")
            for i in range(0, len(led_array), 3):
                r = led_array[i]
                g = led_array[i + 1]
                b = led_array[i + 2]
                # Komma nur, wenn nicht letztes Element
                is_last = i >= len(led_array) - 3
                comma = "" if is_last else ","
                f.write(f"CRGB({r},{g},{b}){comma} \n")
            f.write("}; \n\n")
    except Exception as e:
        print(f"Error while saving the file: {e}")

#===========================================================================================

# Root of the app
@app.route("/", methods=["GET", "POST"])
# Redirects directly to the file_upload page
def redirect_to_page():
    return redirect(url_for("file_upload"))


@app.route("/upload", methods=["GET", "POST"])
def file_upload():
    error = None
    progress = ""
    f = None
    if request.method == "POST":
        f = request.files["file"]
        if f and request.form.get("upload") == "Hochladen":
            f = request.files["file"]
            f.save("./uploads/upload.jpg")
            try:
                for infile in glob.glob(os.path.join("uploads", "*.jpg")):
                    file, ext = os.path.splitext(infile)
                    with Image.open(infile) as im:
                        sourceSizeWidth, sourceSizeHeight = im.size
                        cropFrame = crop_range(sourceSizeWidth, sourceSizeHeight)
                        pixelatedImage = im.resize(
                            size, resample=Image.NEAREST, box=cropFrame
                        )
                        checking_rgb_values(im, size)
                        pixelatedImage = pixelatedImage.resize(
                            (2024, 2024), resample=Image.NEAREST
                        )
                        naming_images(
                            pixelatedImage, sourceSizeWidth, sourceSizeHeight, file
                        )
                        saving_rgb_as_dot_h(led_array, file)
                        led_array.clear()

            except Exception as e:
                print(f"Error while saving the file: {e}")

            progress = "Successfully uploaded!"
            return redirect(url_for("download"))
        else:
            progress = "No image found YET"

    return render_template("index.html", name=name, error=error, progress=progress)


@app.route("/download", methods=["GET", "POST"])
def download():
    if request.method == "POST":
        if request.form.get("redirect") == "Convert another file":
            return redirect(url_for("file_upload"))
        if request.form.get("download") == "Download led_colors.h":
            return send_file("Arduino/TinyArtBoard/led_colors.h", as_attachment=True)

    return render_template("download.html", name=name)


@app.route("/error", methods=["GET", "POST"])
def error():
    if request.method == "POST":
        if request.form.get("back") == "Take me back to the upload!":
            return redirect(url_for("file_upload"))


if __name__ == "__main__":
    app.run(debug=True)
