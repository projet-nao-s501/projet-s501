# -*- coding: utf-8 -*-
# NAO voice recognition + text-to-speech demo
# The robot listens for a command such as:
# "Cherche un t-shirt rouge" and replies with what it understood.

from naoqi import ALProxy
import time
import re


tts = ALProxy("ALTextToSpeech", IP, PORT)
asr = ALProxy("ALSpeechRecognition", IP, PORT)
memory = ALProxy("ALMemory", IP, PORT)

# ------------------------
# Speech Recognition Setup
# ------------------------
asr.setLanguage("French")

# Define known words (vocabulary)
vocabulary = [
    "cherche", "t-shirt", "pantalon", "robe", "chemise",
    "rouge", "noir", "bleu", "blanc", "vert", "jaune"
]
asr.setVocabulary(vocabulary, True)

# ------------------------
# Start Listening
# ------------------------
tts.say("Je t'écoute. Dis-moi ce que je dois chercher.")

asr.subscribe("WordReco")
start_time = time.time()
heard_words = []

while time.time() - start_time < 8:  # Listen for 8 seconds
    data = memory.getData("WordRecognized")
    if data and len(data) > 1:
        word = data[0]
        confidence = data[1]
        if confidence > 0.4 and word not in heard_words:
            heard_words.append(word)
            print("Heard:", word)
    time.sleep(0.5)

asr.unsubscribe("WordReco")

# ------------------------
# Build Sentence from Words
# ------------------------
sentence = " ".join(heard_words)
print("Full recognized sentence:", sentence)

# ------------------------
# Extract Object and Color
# ------------------------
def extract_params(sentence):
    pattern = r"(t-shirt|pantalon|robe|chemise)\s+(rouge|noir|bleu|blanc|vert|jaune)"
    match = re.search(pattern, sentence.lower())
    if match:
        return match.group(1), match.group(2)
    return None, None

obj, color = extract_params(sentence)

# ------------------------
# Respond
# ------------------------
if obj and color:
    tts.say("Tu veux que je cherche un {} {}.".format(obj, color))
else:
    tts.say("Je n'ai pas bien compris ce que tu veux que je cherche.")
