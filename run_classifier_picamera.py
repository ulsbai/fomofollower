import subprocess
import numpy as np
from picamera2.picamera2 import Picamera2
from PIL import Image

FORMAT = 'RGB888'
SIZE = (96, 96)

eye = Picamera2()

config = eye.create_still_configuration()
#config['main']['format'] = FORMAT
config['main']['size'] = SIZE
eye.configure(config)

eye.start()
image_array = eye.capture_array()
eye.stop()

assert image_array.shape == (96, 96, 3), \
   f'Expected Image Array Shape (96, 96, 3), Found {image_array.shape}'

image_data = image_array.tobytes()

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
else:
   print('No bounding box detected')

label_array = image_array.copy()

if cproc.stdout:
   label_array[y:y+height, x, :] = np.full((height, 3), 255)
   label_array[y:y+height, x+width, :] = np.full((height, 3), 255)
   label_array[y, x:x+width, :] = np.full((width, 3), 255)
   label_array[y+height, x:x+width, :] = np.full((width, 3), 255)

label_image = Image.fromarray(label_array)
label_image.save('label.png')
