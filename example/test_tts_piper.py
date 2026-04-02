from picarx.tts import Piper

tts = Piper()

# List supported languages
print(tts.available_countrys())

# Japanese Piper voices are not bundled in this installed package.
# Show all available models, then keep using a validated model that exists.
print(tts.available_models())

# Set a voice model (auto-download if not already present)
tts.set_model("en_US-amy-low")

# Say something
tts.say("こんにちは。Piper TTS のテストです。")
