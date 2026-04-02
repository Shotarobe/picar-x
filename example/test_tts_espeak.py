from picarx.tts import Espeak

tts = Espeak()

# Optional voice tuning
# tts.set_amp(100)   # 0 to 200
# tts.set_speed(150) # 80 to 260
# tts.set_gap(5)     # 0 to 200
# tts.set_pitch(50)  # 0 to 99

# Quick hello (sanity check)
tts.say("Hello! I'm Espeak TTS.")
