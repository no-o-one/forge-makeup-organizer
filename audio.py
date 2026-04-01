from openai import OpenAI
from gpiozero import Button, OutputDevice
import subprocess
import time

m1_pins = [OutputDevice(17), OutputDevice(4), OutputDevice(3), OutputDevice(2)]
m2_pins = [OutputDevice(27), OutputDevice(22), OutputDevice(10), OutputDevice(9)]
m3_pins = [OutputDevice(11), OutputDevice(5), OutputDevice(6), OutputDevice(13)]

b1_is_open = False
b2_is_open = False
b3_is_open = False

#possible inputs for those are l - lipstick, b - blush, r - ring, h - hair tie, e - eye liner, c - concealer
items_b1 = [];
items_b2 = [];
items_b3 = [];

step_stage = 0 #global var for the do one step funct
def doOneStep(dir, pins): #assuming dir is boolean and pins is a list of pins of the motor from in1 to in4
    global step_stage
    if dir:
        for pin in pins:
            if pins.index(pin) == step_stage:
                pin.on()
            else:
                pin.off()
    else:
        for pin in pins:
            if pins.index(pin) == step_stage:
                pins[3-pins.index(pin)].on()
            else:
                pins[3-pins.index(pin)].off()

    step_stage +=1
    if step_stage>3:
        step_stage = 0

def rotate(pins, dir, amount_of_steps):
    for i in range(amount_of_steps):
        doOneStep(dir, pins)
        time.sleep(0.003)


client = OpenAI(api_key='[key]')
button = Button(19)
led = OutputDevice(26)

def check_transcript(tr):
    global b1_is_open
    global b2_is_open
    global b3_is_open
    print("checking input")
    if "box" in tr and "open" in tr and ("one" in tr or "1" in tr or "left" in tr or "concealer" in tr) and b1_is_open == False:
        rotate(m1_pins, True, 4000)
        b1_is_open = True
    elif "box" in tr and "close" in tr and ("one" in tr or "1" in tr or "left" in tr or "concealer" in tr) and b1_is_open == True:
        print("closing box one")
        rotate(m1_pins, False, 4000)
        b1_is_open = False
    elif "box" in tr and "open" in tr and ("two" in tr or "2" in tr or "middle" in tr or "lipstick" in tr) and b2_is_open == False:
        print("opening box 2")
        rotate(m2_pins, True, 4000)
        b2_is_open = True
    elif "box" in tr and "close" in tr and ("two" in tr or "2" in tr or "middle" in tr or "lipstick" in tr) and b2_is_open == True:
        rotate(m2_pins, False, 4000)
        b2_is_open = False
    elif "box" in tr and "open" in tr and ("three" in tr or "3" in tr or "right" in tr or "ring" in tr) and b3_is_open == False:
        rotate(m3_pins, True, 4000)
        b3_is_open = True
    elif "box" in tr and "close" in tr and ("three" in tr or "3" in tr or "right" in tr or "ring" in tr) and b3_is_open == True:
        rotate(m3_pins, False, 4000)
        b3_is_open = False
    elif "open" in tr and "all" in tr and "box" in tr:
        if not b1_is_open:
            rotate(m1_pins, True, 4000)
            b1_is_open = True
        if not b2_is_open:
            rotate(m2_pins, True, 4000)
            b2_is_open = True
        if not b3_is_open:
            rotate(m3_pins, True, 4000)
            b3_is_open = True
    elif "close" in tr and "all" in tr and "box" in tr:
        print('detecting')
        if b1_is_open:
            rotate(m1_pins, False, 4000)
            print('one')
            b1_is_open = False
        if b2_is_open:
            rotate(m2_pins, False, 4000)
            print('two')
            b2_is_open = False
        if b3_is_open:
            rotate(m3_pins, False, 4000)
            print('three')
            b3_is_open = False

def get_transcript():
    audio_file = open("./output.wav", "rb")
    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
    print(transcription)
    check_transcript(transcription.lower())


def start_recording():
    time.sleep(0.5)
    if button.is_pressed:
        print("pressed")
        led.on()
        subprocess.run(["./audio_recorder.sh", "start"])

def stop_recording():
    time.sleep(0.5)
    if not button.is_pressed:
        print("released")
        led.off()
        try:
            subprocess.run(["./audio_recorder.sh", "stop"])
        except Exception as e:
            pass
            #print(e)
        try:
            get_transcript()
        except Exception as e:
            print(e)


#button.when_pressed = start_recording
#button.when_released = stop_recording

is_recording = False

while 1:
    if button.is_pressed:
        time.sleep(1)
        if button.is_pressed:
            is_recording = True
            start_recording()
            while is_recording:
                if not button.is_pressed:
                    time.sleep(1)
                    if not button.is_pressed:
                        is_recording = False
                        stop_recording()
