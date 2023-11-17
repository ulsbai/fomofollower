# Fomofollower

The fomofollower is a program that I made that drives a robot around to follow my red shirt. It uses an artificial intelligence model that I trained using [Edge Impulse](https://edgeimpulse.com) and deployed as a C++ library. Currently it can drive a snap circuit rover and a Freenove Smart Car for Raspberry Pi.

# Setup for a Freenove Smart Car for Raspberry Pi

1. Purchase a Freenove Smart Car for Raspberry Pi

2. Follow Freenove's tutorial for [ordinary wheels](https://github.com/Freenove/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/blob/master/Tutorial(ordinary_wheels).pdf) or [mechanum wheels](https://github.com/Freenove/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/blob/master/Tutorial(mecanum_wheels).pdf). This will require you to purchase a raspberry pi and a memory card.

3. Ssh your new raspberry pi from step 2, newly setup and with Freenove's library installed. From the home directory, clone my repository with:

      ``git clone https://github.com/ulsbai/fomofollower``

4. Type the following commands to copy my code into the smart car server code (Freenove's code):

      - ``cp fomofollower/app Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server/fomofollower_app``
      - ``cp fomofollower/drive_smart_car_fomofollower.py Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server``

5. Change the current directory to Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server with:

      ``cd Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server``

6. Put the smart car on the ground and start the fomofollower with:

      ``python drive_smart_car_fomofollower.py 500``
   
   The 500 is a constant that defines how sharply the robot rotates. You can try adjusting it if you want.

7. Wear a bright red shirt and stand in front of the smart car's camera, and the smart car should start going toward you!
