#include <iostream>
#include <fstream>
#include "edge-impulse-sdk/classifier/ei_run_classifier.h"

using namespace std;

int main()
{
   char char_buf[3 * EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
   char byte;
   
   for (uint32_t i = 0; i < (3 * EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE); i++)
   {
      if (!cin.get(byte)){
         cout << "Failed to read byte" << endl;
         return 1;
      }
      
      char_buf[i] = byte;
   }
   
   cerr << "Built character buffer" << endl;
   
   float float_buf[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
   
   for (uint32_t i = 0; i < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; i++)
   {
      uint32_t r = (uint32_t)char_buf[i * 3];
      uint32_t g = (uint32_t)char_buf[i * 3 + 1];
      uint32_t b = (uint32_t)char_buf[i * 3 + 2];
      float_buf[i] = (float)((r << 16) | (g << 8) | b);
   }
   
   cerr << "Built floating-point buffer" << endl;
   
   signal_t signal;
   numpy::signal_from_buffer(float_buf, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
   
   ei_impulse_result_t result;
   EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);
   
   if (res != EI_IMPULSE_OK)
   {
      cerr << "Failed to run classifier" << endl;
      return 1;
   }
   
#if EI_CLASSIFIER_OBJECT_DETECTION != 1
   cerr << "Not object detection" << endl;
   return 1;
#endif
   
   cerr << "Object detection count: " << EI_CLASSIFIER_OBJECT_DETECTION_COUNT << endl;
   
   ei_impulse_result_bounding_box_t box = result.bounding_boxes[0];
   
   if (box.value != 0)
   {
      cout << box.value << ' ' << box.x << ' ' << box.y << ' ' << box.width << ' ' << box.height;
      
      cerr << "Bounding box #0 Label: " << box.label << " Value: " << box.value << " X: " << box.x
      << " Y: " << box.y << " Width: " << box.width << " Height: " << box.height << endl;
   }
}
