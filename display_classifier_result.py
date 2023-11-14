import subprocess
import numpy as np
from PIL import Image
import os

TRAINING_SET_TO_BE_DISPLAYED_DIRECTORY = '/home/pi/fomofollower_ipad_pictures'

for filename in os.listdir(TRAINING_SET_TO_BE_DISPLAYED_DIRECTORY):
   assert os.path.isfile(os.path.join(TRAINING_SET_TO_BE_DISPLAYED_DIRECTORY, filename))
   
   with open(os.path.join(TRAINING_SET_TO_BE_DISPLAYED_DIRECTORY, filename), 'rb') as f:
      image_data = f.read()

   cproc = subprocess.run(['./app'], input=image_data, stdout=subprocess.PIPE)

   if cproc.returncode:
      raise RuntimeError(f'C++ subprocess completed with non-zero return code {cproc.returncode}')

   if cproc.stdout:
      value, x, y, width, height = cproc.stdout.decode().split(' ')
      value = float(value)
      x = int(x)
      y = int(y)
      width = int(width)
      height = int(height)
      
   label_array = np.frombuffer(image_data, dtype=np.uint8).copy().reshape(96, 96, 3)
   
   if cproc.stdout:
      label_array[y:y+height, x, :] = np.full((height, 3), 255)
      label_array[y:y+height, x+width, :] = np.full((height, 3), 255)
      label_array[y, x:x+width, :] = np.full((width, 3), 255)
      label_array[y+height, x:x+width, :] = np.full((width, 3), 255)
   
   label_image = Image.fromarray(label_array, 'RGB')
   
   label_image.show()
