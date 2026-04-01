#!/bin/bash

# Global variable to store the PID of the recording process
RECORDING_PID=""
# File to store the temporary audio data
TEMP_FILE="/tmp/temp_audio.wav"

# Function to start recording
start_recording() {
    echo "Starting audio recording..."
    # Start recording in the background using arecord
    arecord -f cd -r 12000 -t wav "$TEMP_FILE" &
    RECORDING_PID=$!
    echo "Recording started. PID: $RECORDING_PID"
}

# Function to stop recording and save to desired file
save_recording() {
    echo "PID $RECORDING_PID and latest bg proces is"
    echo $!
    RECORDING_PID=$(pgrep -f "arecord -f cd -r 12000 -t wav /tmp/temp_audio.wav")
    if [ -n "$RECORDING_PID" ]; then
        echo "Stopping recording..."
        kill "$RECORDING_PID"
        wait "$RECORDING_PID" 2>/dev/null
        OUTPUT_FILE="output.wav"
        mv "$TEMP_FILE" "$OUTPUT_FILE"
        echo "Recording saved as $OUTPUT_FILE"
        RECORDING_PID=""
    else
        echo "No recording in progress."
    fi
}

# Uncomment below lines to test directly when running the script
# start_recording
# sleep 5
# save_recording

# to make it possible to pass an arg
case "$1" in
    start)
        start_recording
        ;;
    stop)
        save_recording
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        ;;
esac