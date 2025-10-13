import time

def func(session):
    tts = session.service("ALTextToSpeech")
    tts.say("Naherry le plus doué")

def run_asr(session):
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
    
    # Set language to English
    asr.setLanguage("English")
    
    # Example: Adds "yes", "no" and "please" to the vocabulary (without wordspotting)
    vocabulary = ["yes", "no", "please"]
    asr.setVocabulary(vocabulary, False)
    asr.getAudioExpression()
    
    # Start the speech recognition engine with user Test_ASR
    asr.subscribe("Test_ASR")
    print('Speech recognition engine started')
    
    for  i in [0,36,72,108,144,180,216,252,288,324] :
        rightData = memory.getData(f"Device/SubDeviceList/Ears/Led/Right/{i}Deg/Actuator/Value")
        leftData = memory.getData(f"Device/SubDeviceList/Ears/Led/Left/{i}Deg/Actuator/Value")
        print(f"paroles dites : droite : {rightData} gauche : {leftData} ")
    time.sleep(20)
    
    # Stop the speech recognition engine
    asr.unsubscribe("Test_ASR")
    print('Speech recognition engine stopped')

# Example usage:
# session = qi.Session()
# session.connect("tcp://<robot_ip>:9559")
# func(session)
# run_asr(session)
