#!/bin/bash

# Reset the JSON folder
cd output
rm -rf json
mkdir json
cd ../../openpose

# Run OpenPose on videos
./build/examples/openpose/openpose.bin --video ../Cameras/output/output_open_eyes.mp4 --display 0 --write_video  ../Cameras/output/processed_output_open_eyes.avi --write_json  ../Cameras/output/json
./build/examples/openpose/openpose.bin --video ../Cameras/output/output_closed_eyes.mp4 --display 0 --write_video  ../Cameras/output/processed_output_closed_eyes.avi --write_json  ../Cameras/output/json

# Delete unprocessed videos
rm ../Cameras/output/output_open_eyes.mp4
rm ../Cameras/output/output_closed_eyes.mp4
