#include <iostream>
#include <fstream>
#include "edge-impulse-sdk/classifier/ei_run_classifier.h"

using namespace std;

int main()
{
   ifstream image_file;
   image_file.open("/home/pi/image.rgb", ios_base::binary);
   
   if (!image_file.is_open())
   {
      cout << "Image file not opened" << endl;
      return 1;
   }
   
   image_file.seekg(0, ios::end);
   int length = image_file.tellg();
   image_file.seekg(0, ios::beg);
   
   if (length != 3 * EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE)
   {
      cout
      << "The length of the image file is not the same as three times the expected input frame size"
      << " Image file length: " << length << " Expected input frame size: "
      << EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE << " 3 * Expected input frame size: "
      << 3 * EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE << endl;
      return 1;
   }
   
   char* char_buf = new char[length];
   image_file.read(char_buf, length);
   image_file.close();
   
   cout << "Passed char_buf read" << endl;
   
   float float_buf[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
   
   for (uint32_t i = 0; i < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; i++)
   {
      uint32_t r = (uint32_t)char_buf[i * 3];
      uint32_t g = (uint32_t)char_buf[i * 3 + 1];
      uint32_t b = (uint32_t)char_buf[i * 3 + 2];
      float_buf[i] = (float)((r << 16) | (g << 8) | b);
   }
   
   cout << "Passed float_buf build" << endl;
   
   signal_t signal;
   numpy::signal_from_buffer(float_buf, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
   
   ei_impulse_result_t result;
   EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);
   
   if (res != EI_IMPULSE_OK)
   {
      cout << "Failed to run classifier" << endl;
      return 1;
   }
   
#if EI_CLASSIFIER_OBJECT_DETECTION != 1
   cout << "Not object detection" << endl;
   return 1;
#endif
   
   cout << "Object detection count: " << EI_CLASSIFIER_OBJECT_DETECTION_COUNT << endl;
   
   for (uint32_t i = 0; i < EI_CLASSIFIER_OBJECT_DETECTION_COUNT; i++)
   {
      ei_impulse_result_bounding_box_t box = result.bounding_boxes[i];
      
      if (box.value == 0)
      {
         cout << "Box value is 0" << endl;
         continue;
      }
      
      cout << "Bounding box #" << i << " Label: " << box.label << " Value: " << box.value << " X: "
      << box.x << " Y: " << box.y << " Width: " << box.width << " Height: " << box.height << endl;
   }
   
   return 0;
}
