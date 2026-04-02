from picarx import Picarx
import time

# === TTS Configuration ===
# Default: Piper
from picarx.tts import Piper
tts = Piper()
tts.set_model("en_US-amy-low")  # this package has no bundled Japanese Piper voice

# Optional: switch to OpenAI TTS
# from picarx.tts import OpenAI_TTS
# from secret import OPENAI_API_KEY
# tts = OpenAI_TTS(api_key=OPENAI_API_KEY)
# tts.set_model("gpt-4o-mini-tts")  # low-latency TTS model
# tts.set_voice("alloy")            # choose a voice

# === PiCar-X Setup ===
px = Picarx()

# Quick hello (sanity check)
tts.say("こんにちは。Piper で話す PiCar-X です。")

def main():
    try:
        # Leg 1
        px.forward(30)
        time.sleep(3)
        px.stop()
        tts.say("鼻が30センチになれないのはどうしてでしょう。長すぎると足になってしまうからです。")

        # Leg 2
        px.forward(30)
        time.sleep(3)
        px.stop()
        tts.say("牛が宇宙へ行ったのはなぜでしょう。ムーンを見に行くためです。")

        # Wrap-up
        tts.say("今日はここまでです。さようなら。帰って休みましょう。")
        px.backward(30)
        time.sleep(6)
        px.stop()

    except KeyboardInterrupt:
        px.stop()
    finally:
        px.stop()
        px.set_dir_servo_angle(0)

if __name__ == "__main__":
    main()
