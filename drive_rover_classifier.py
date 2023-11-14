from RPi import GPIO as gpio
import subprocess
import numpy as np
from picamera2.picamera2 import Picamera2
import time
from PIL import Image
import sys

SIZE = (96, 96)

eye = Picamera2()

config = eye.create_still_configuration()
config['main']['size'] = SIZE
eye.configure(config)

gpio.setmode(gpio.BCM)

MOTOR_CONTROLLER_PINS = 17, 27, 22, 23, 24, 25
MAX_MOVING_OBJECT_DETECTION_ATTEMPTS = 3
#MAX_STOPPED_OBJECT_DETECTION_ATTEMPTS = 8
#MAX_SCAN_MOVING_OBJECT_DETECTION_ATTEMPTS = 1
#MAX_SCAN_STOPPED_OBJECT_DETECTION_ATTEMPTS = 3

CLASSIFIER_INTERVAL = 0.5

DIRECTION_TERM = 30
DIRECTION_FACTOR = 0.3

def go(direction):
   print('Going Direction:', direction)
   
   left = -direction
   right = direction
   speed = 100 - max(left, right)
   left += speed
   right += speed
   
   print('Left:', left, 'Right:', right)
   
   if left >= 0:
      gpio.output(MOTOR_CONTROLLER_PINS[1], gpio.LOW)
      gpio.output(MOTOR_CONTROLLER_PINS[2], gpio.HIGH)
   else:
      gpio.output(MOTOR_CONTROLLER_PINS[1], gpio.HIGH)
      gpio.output(MOTOR_CONTROLLER_PINS[2], gpio.LOW)
      left = -left
   
   if right >= 0:
      gpio.output(MOTOR_CONTROLLER_PINS[3], gpio.LOW)
      gpio.output(MOTOR_CONTROLLER_PINS[4], gpio.HIGH)
   else:
      gpio.output(MOTOR_CONTROLLER_PINS[3], gpio.HIGH)
      gpio.output(MOTOR_CONTROLLER_PINS[4], gpio.LOW)
      right = -right
      
   left_pwm.ChangeDutyCycle(left)
   right_pwm.ChangeDutyCycle(right)

def stop():
   print('Stopping')
   gpio.output(MOTOR_CONTROLLER_PINS[2], gpio.LOW)
   gpio.output(MOTOR_CONTROLLER_PINS[4], gpio.LOW)
   return ''

def capture_image():
   global image_array
   image_array = eye.capture_array()
   return image_array.tobytes()

def run_classifier(image_data):   
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
      
      print('Detected bounding box Value:', value, 'X:', x, 'Y:', y, 'Width:', width, 'Height:', height)
      
      return value, x, y, width, height
   
   else:
      print('No bounding box detected')
      
      return None

def go_classifier():
   predictions = run_classifier(capture_image())
   
   if predictions:
      value, x, y, width, height = predictions
      
      global centrex
      centrex = x + 0.5 * width
      
      direction = centrex - 0.5 * SIZE[0]
      direction *= 100 - DIRECTION_TERM
      direction /= 0.5 * SIZE[0]
      direction *= DIRECTION_FACTOR
      if direction > 0:
         direction += DIRECTION_TERM
      elif direction < 0:
         direction -= DIRECTION_TERM
      if direction > 100:
         direction = 100
      elif direction < -100:
         direction = -100
      
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
   gpio.cleanup()
   
   image = Image.fromarray(image_array, 'RGB')
   image.save('label.png')

try:
   gpio.setmode(gpio.BCM)
   for pin in MOTOR_CONTROLLER_PINS:
      gpio.setup(pin, gpio.OUT)
   
   gpio.output(MOTOR_CONTROLLER_PINS[1], gpio.LOW)
   gpio.output(MOTOR_CONTROLLER_PINS[2], gpio.HIGH)
   gpio.output(MOTOR_CONTROLLER_PINS[3], gpio.LOW)
   gpio.output(MOTOR_CONTROLLER_PINS[4], gpio.HIGH)
   
   left_pwm = gpio.PWM(MOTOR_CONTROLLER_PINS[0], 50)
   right_pwm = gpio.PWM(MOTOR_CONTROLLER_PINS[5], 50)
   left_pwm.start(0)
   right_pwm.start(0)
   
   if __name__=='__main__':
      eye.start()
      
      no_bounding_box_detected_count = 0
      #state = 'starting' # 'starting', 'stopped', 'moving',
      #                  # 'ready_to_scan', 'scanning_left', 'scanning_stopped, 'scanning_right',
      #                  # 'finished_scanning'
      
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
            #state = 'stopped'
            #no_bounding_box_detected_count = 0
         
         #if state == 'stopped' and no_bounding_box_detected_count == MAX_STOPPED_OBJECT_DETECTION_ATTEMPTS:
            #state = 'ready_to_scan'
            #scan(state)
            #state = 'scanning_right'
            #no_bounding_box_detected_count = 0
         
         #if state == 'scanning_right' and \
               #no_bounding_box_detected_count == MAX_SCAN_MOVING_OBJECT_DETECTION_ATTEMPTS:
            #scan(state)
            #state = 'scanning_stopped'
            #no_bounding_box_detected_count = 0
        
         #if state == 'scanning_stopped' and \
               #no_bounding_box_detected_count == MAX_SCAN_STOPPED_OBJECT_DETECTION_ATTEMPTS:
            #scan(state)
            #state = 'scanning_left'
            #no_bounding_box_detected_count = 0
        
         #if state == 'scanning_left' and \
               #no_bounding_box_detected_count == 2 * MAX_SCAN_MOVING_OBJECT_DETECTION_ATTEMPTS:
            #scan(state)
            #state = 'finished_scanning'
            #no_bounding_box_detected_count = 0

finally:   
   cleanup()
