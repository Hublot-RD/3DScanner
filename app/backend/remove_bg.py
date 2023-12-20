# Importing Required Modules 
from rembg import remove        # BUG: does not work because of SSL authentication error
from PIL import Image 
  
# Store path of the image in the variable input_path 
OBJECT_NAME = "Pot_blanc"
IMAGE_COUNT = 30
input_files = []
output_files = []
for i in range(IMAGE_COUNT):
    input_path = f"C:/Users/v.philippoz/Documents/scanner3D/{OBJECT_NAME}/{OBJECT_NAME}_" + "{:03d}.jpg".format(i+1)
    output_path = f"C:/Users/v.philippoz/Documents/scanner3D/{OBJECT_NAME}/{OBJECT_NAME}_" + "{:03d}_bg.jpg".format(i+1)
    input_files.append(input_path)
    output_files.append(output_path)

  
# Processing the image 
for i, input_path in enumerate(input_files):
    input = Image.open(input_path) 
    
    # Removing the background from the given Image 
    output = remove(input) 
    output_path = output_files[i]

    #Saving the image in the given path 
    output.save(output_path)
  
  