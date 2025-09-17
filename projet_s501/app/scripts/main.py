"""
An example of a Python Script as an app for NAO/Pepper
"""

__version__ = "0.1.0"

__author__ = 'Naherry'
__email__ = 'modaherry@gmail.com'

import qi

class Activity:
    "A sample standalone app, that demonstrates simple Python usage"
    APP_ID = "projet_s501"
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.session = qiapp.session

    def on_start(self):
        try:
            self.session.service("ALTextToSpeech").say("Hello everybody! check out my eyes")
            self.session.service("ALLeds").rasta(2.0)
            self.session.service("ALTextToSpeech").say("Neat wasn't it?")
            self.session.service("ALMotion").wakeUp()
            self.session.service("ALRobotPosture").goToPosture("LyingBelly", 1.0)
        finally:
            # Note, until we do this, this will run forever (which is sometimes what we want)
            self.stop()

    def stop(self):
        "Standard way of stopping the application."
        self.qiapp.stop()

if __name__ == "__main__":
    try :
        qiapp = qi.Application()
        qiapp.start()
        activity = Activity(qiapp)
        qi.runAsync(activity.on_start)
        qiapp.run()
    except Exception as e :
        print(e)