# About the Project

  This project was completed on a freelance basis, and within the stipulated time frame of 6 - 8 months.
  We use RTSP camera to track incoming and outgoing ships, and raise an alarm at docks when an object/ship approaches too close to the Fenders.

## D@rknet Architecture
We built the darknet model on windows and DLL files for CUDA 10.1 and 11.0 are included.
If GPU/CUDA is not availabel use the *_no_gpu.dll* file. the dll files have been built using OPENCV

## Implementation
1. We stated with yolov3 model, thought the accuracy was high, the Arcitecture failed while while deploying the model as multi-threading.
2. We then mmoved forwand with Yolov3-tiny.
3. The weight files for yolov3-tiny is included in the repository.

4 . (updated Oct, 2021) : the final actitecture of tiny-yolo v3 has been improved using fire layers.
5 . Multithreading was implemented to process frames from 4 different RTSP streams.
