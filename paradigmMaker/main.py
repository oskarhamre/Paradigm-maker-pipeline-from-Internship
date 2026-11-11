from storycreation_and_text_to_speech import generate_story_and_sound
from splitAudio import splitAudio
from generateJson import generate_json

language = "English"
story_name = "BaselineTest"
story_theme = ""

def create_paradigm(lang: str, storyName: str, storyTheme: str = "") -> None:
    """
    Makes a paradigm folder containing audiofiles for each block and a complete JSON-file.
    Note that the folder does not contain a pictures-folder. This should be copy-pasted into the folder
    before downloading to nordicAktiva.

    Parameters
    ---
    lang: str
        Language in which to generate the story
    storyName: str
        Name of the story. This will also be used as the name
        of the paradigm: Pediatric StoryListening_{storyName}
    storyTheme: str, default=""
        Theme of the story. If left blank, the theme of the story
        will be native to the language spesified in lang
    """
    generate_story_and_sound(lang, storyName, storyTheme)
    splitAudio(storyName)
    generate_json(lang, storyName)
    print(f"\n\nParadigm {story_name} created:)\n")

if __name__ == "__main__":
    create_paradigm(language, story_name, story_theme)