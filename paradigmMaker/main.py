from storycreation_and_text_to_speech import generate_story_and_sound
from splitAudio import splitAudio
from generateJson import generate_json

language = "English"
story_name = "BaselineTest"
story_theme = ""

def create_paradigm(lang: str, storyName: str, storyTheme: str):
    # generate_story_and_sound(lang, storyName, storyTheme)
    # splitAudio(storyName)
    generate_json(lang, storyName)
    print(f"\n\nParadigm {story_name} created:)\n")

if __name__ == "__main__":
    create_paradigm(language, story_name, story_theme)