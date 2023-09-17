from functions import *

dataset_path = "/Users/ceadar/Downloads/Firmex 23-09-14 075346/10.3.1_Lease 14-16 Parkgate Street, D 8.pdf"
print('Processing the PDF file')
contents = extract_pdf_from_image(dataset_path)
print(contents)
