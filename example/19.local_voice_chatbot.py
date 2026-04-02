import re
import subprocess
import time
from pathlib import Path
from picarx.llm import Ollama
from picarx.stt import Vosk

stt = Vosk(language="ja")

OPEN_JTALK_DIC = Path("/var/lib/mecab/dic/open-jtalk/naist-jdic")
OPEN_JTALK_VOICE = Path("/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice")


class OpenJTalkTTS:
    def __init__(self, dic_path: Path, voice_path: Path) -> None:
        if not dic_path.exists():
            raise FileNotFoundError(f"Dictionary not found: {dic_path}")
        if not voice_path.exists():
            raise FileNotFoundError(f"Voice not found: {voice_path}")
        self.dic_path = dic_path
        self.voice_path = voice_path

    def say(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        wav_path = "/tmp/open_jtalk.wav"
        subprocess.run(
            [
                "open_jtalk",
                "-x", str(self.dic_path),
                "-m", str(self.voice_path),
                "-r", "1.0",
                "-ow", wav_path,
            ],
            input=text,
            text=True,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["aplay", "-q", wav_path],
            check=True,
            capture_output=True,
        )


tts = OpenJTalkTTS(OPEN_JTALK_DIC, OPEN_JTALK_VOICE)

INSTRUCTIONS = (
    "You are a helpful assistant. Answer directly in natural Japanese. "
    "Return only the answer itself in natural Japanese. "
    "Do NOT include any hidden thinking, analysis, markdown, or tags like <think>."
)
WELCOME = "こんにちは。音声チャットボットです。準備ができたら話してください。"

# --- INIT (set your host IP/model) ---
# If Ollama runs on the same Pi, use "localhost".
# If it runs on another computer in your LAN, replace with that computer's LAN IP.
llm = Ollama(ip="localhost", model="llama3.2:3b")
llm.set_max_messages(20)
llm.set_instructions(INSTRUCTIONS)

def strip_thinking(text: str) -> str:
    """Remove any chain-of-thought sections and stray markers."""
    if not text:
        return ""
    text = re.sub(r"<\s*think[^>]*>.*?<\s*/\s*think\s*>", "", text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r"<\s*thinking[^>]*>.*?<\s*/\s*thinking\s*>", "", text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r"```(?:\s*thinking)?\s*.*?```", "", text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r"\[/?thinking\]", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+\n", "\n", text).strip()


def parse_reply(text: str) -> str:
    """Extract the Japanese reply from the LLM response."""
    clean = strip_thinking(text)
    clean = re.sub(r"(?is)^\s*(jp|say|romaji)\s*:\s*", "", clean)
    clean = re.sub(r"(?im)^\s*(jp|say|romaji)\s*:\s*", "", clean)
    return clean.strip()


def should_ignore_input(text: str, last_spoken: str) -> bool:
    """Drop obvious self-captured or garbage transcripts."""
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    if not normalized:
        return True

    garbage_markers = (
        "japanese letter",
        "chinese letter",
        "japanese letters",
        "chinese letters",
        "cjk",
        "unicode",
    )
    if any(marker in normalized for marker in garbage_markers):
        return True

    last_normalized = re.sub(r"\s+", " ", last_spoken).strip().lower()
    if last_normalized and normalized == last_normalized:
        return True

    return False

def main():
    print(WELCOME)
    tts.say(WELCOME)
    last_spoken = WELCOME

    try:
        while True:
            print("\n🎤 音声入力待機中... (Ctrl+C で終了)")

            # Collect final transcript from Vosk
            text = ""
            for result in stt.listen(stream=True):
                if result["done"]:
                    text = result["final"].strip()
                    print(f"[YOU] {text}")
                else:
                    print(f"[YOU] {result['partial']}", end="\r", flush=True)

            if not text:
                print("[INFO] 音声を認識できませんでした。もう一度話してください。")
                time.sleep(0.1)
                continue

            if should_ignore_input(text, last_spoken):
                print("[INFO] 自己音声または無効な認識結果を無視しました。")
                time.sleep(0.2)
                continue

            # Query LLM with streaming
            reply_accum = ""
            response = llm.prompt(text, stream=True)
            for next_word in response:
                if next_word:
                    reply_accum += next_word

            display_text = parse_reply(reply_accum)
            if display_text:
                print(f"[BOT] {display_text}")
                tts.say(display_text)
                last_spoken = display_text
                time.sleep(0.4)
            else:
                fallback = "すみません。うまく聞き取れませんでした。"
                tts.say(fallback)
                last_spoken = fallback

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n[INFO] 停止します...")
    finally:
        tts.say("終了します。")
        print("Bye.")

if __name__ == "__main__":
    main()
