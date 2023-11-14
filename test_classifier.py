import subprocess

with open('/home/pi/image.rgb', 'rb') as f:
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
else:
   raise RuntimeError('No bounding box found')

print('Value:', value, 'X:', x, 'Y:', y, 'Width:', width, 'Height:', height)
