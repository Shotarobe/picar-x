from picarx.stt import Vosk

vosk = Vosk(language="ja")

print(vosk.available_languages)

while True:
    print("何か話してください")
    result = vosk.listen(stream=False)
    print(result)
