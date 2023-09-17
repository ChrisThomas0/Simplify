from pdf2image import convert_from_path
import easyocr
import numpy as np
import time
import fitz
import pdfplumber
import keras_ocr


def easy_ocr(file_path):
    content_string = ''
    images = convert_from_path(file_path, dpi=200)

    for i, image in enumerate(images):
        image_array = np.array(image)
        results = reader.readtext(image_array, detail=0,
                                  slope_ths=0.1, ycenter_ths=0.5,
                                  height_ths=0.5, width_ths=0.5,
                                  add_margin=0.1, x_ths=1.0,
                                  y_ths=0.5, paragraph=True)
        content_string += ' '.join(result for result in results)
    return content_string


def keras_ocr_extractor(file_path):
    before_converting_image = time.time()
    pdf_converted_image = convert_from_path(file_path, dpi=400)
    after_converting_image = time.time()
    print(f'Total time to convert PDF to images is  {after_converting_image - before_converting_image}')

    pdf_converted_image[0].save('First_page.jpg')

    pipeline = keras_ocr.pipeline.Pipeline()

    images = [keras_ocr.tools.read(img) for img in [
        './First_page.jpg'
    ]]

    prediction_groups = pipeline.recognize(images)
    print('Prediction groups', prediction_groups)
    return True


def pymu_pdf(file_path):
    doc = fitz.open(file_path)
    print(f'Document is {doc}')
    for page in doc:
        text = page.get_text()
    return text


def pdf_plumber(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        print('page is ', page)
        text = page.extract_text()
    return text


def write_contents(contents, file_name):
    output_file = './../../results/' + file_name
    with open(output_file, 'w') as f:
        f.write(contents)


reader = easyocr.Reader(['en'], gpu=True, quantize=True)
test_file_1 = '/Users/ceadar/Documents/WallaceCorp/Project/ocr/dataset/First_Ireland/10.9.7.23_Aviva TOBA.pdf'
test_file_2 = '/Users/ceadar/Documents/WallaceCorp/Project/ocr/dataset/First_Ireland/10.7.1_Revenue TWSS Enquiry ' \
              '-Closure-Letter-1 14.04.2021.pdf'
easy_ocr_contents = easy_ocr(test_file_1)
print('easy_ocr_contents', easy_ocr_contents)
