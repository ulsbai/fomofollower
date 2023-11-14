from Motor import Motor
import subprocess
import numpy as np
from picamera2.picamera2 import Picamera2
import time
from PIL import Image
import math
import sys

SIZE = (96, 96)

eye = Picamera2()

config = eye.create_still_configuration()
config['main']['size'] = SIZE
eye.configure(config)

pwm = Motor()

MOTOR_CONTROLLER_PINS = 17, 27, 22, 23, 24, 25
MAX_MOVING_OBJECT_DETECTION_ATTEMPTS = 1

CLASSIFIER_INTERVAL = 0.1

DIRECTION_FACTOR = int(sys.argv[1])

SPEED = 1000

def go(direction):
   print('Going Direction:', direction)
   
   left = SPEED + direction
   right = SPEED - direction
   
   print('Left:', left, 'Right:', right)
   
   pwm.setMotorModel(left, left, right, right)

def stop():
   print('Stopping')
   pwm.setMotorModel(0, 0, 0, 0)
   return ''

def capture_image():
   global image_array
   image_array = eye.capture_array()
   return image_array.tobytes()

def run_classifier(image_data):   
   cproc = subprocess.run(['./fomofollower_app'], input=image_data, stdout=subprocess.PIPE)
   
   if cproc.returncode:
      raise RuntimeError(f'C++ subprocess completed with non-zero return code {cproc.returncode}')
   
   
   if cproc.stdout:
      value, x, y, width, height = cproc.stdout.decode().split(' ')
      value = float(value)
      x = int(x)
      y = int(y)
      width = int(width)
      height = int(height)
      
      print('Detected bounding box Value:', value, 'X:', x, 'Y:', y, 'Width:', width, 'Height:', height)
      
      return value, x, y, width, height
   
   else:
      print('No bounding box detected')
      
      return None

def go_classifier():
   predictions = run_classifier(capture_image())
   
   if predictions:
      value, x, y, width, height = predictions
      
      centrex = x + 0.5 * width
      
      direction = (centrex - 0.5 * SIZE[0]) / (0.5 * SIZE[0])
      direction *= DIRECTION_FACTOR
      direction = math.floor(direction)
      
      go(direction)
      
      return True
   
   else:
      return False

def scan(state):
   print('State:', state)
   
   if state == 'ready_to_scan':
      go(100)
   elif state == 'scanning_right':
      stop()
   elif state == 'scanning_stopped':
      go(-100)
   elif state == 'scanning_left':
      stop()

def cleanup():
   stop()
   eye.stop()
   
   image = Image.fromarray(image_array, 'RGB')
   image.save('label.png')

try:
   if __name__=='__main__':
      eye.start()
      
      no_bounding_box_detected_count = 0
      
      while True:
         time.sleep(CLASSIFIER_INTERVAL)
         
         if go_classifier():
            #state = 'moving'
            no_bounding_box_detected_count = 0
         else:
            no_bounding_box_detected_count += 1
         
         #if state == 'moving' and no_bounding_box_detected_count == MAX_MOVING_OBJECT_DETECTION_ATTEMPTS:
         if no_bounding_box_detected_count == MAX_MOVING_OBJECT_DETECTION_ATTEMPTS:
            stop()

finally:
   cleanup()
