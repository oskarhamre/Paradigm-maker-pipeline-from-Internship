import os
from anthropic import Anthropic
import requests
from dotenv import load_dotenv
from pathlib import Path
from pydub import AudioSegment

#Languages available, the code for the language chosen is sent to the api
LANGUAGE_CODES = {
    "Arabic": "ar",
    "Bulgarian": "bg",
    "Chinese": "zh",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Filipino": "fil",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Hindi": "hi",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Malay": "ms",
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Slovak": "sk",
    "Spanish": "es",
    "Swedish": "sv",
    "Tamil": "ta",
    "Turkish": "tr",
    "Ukrainian": "uk"
}

TOKEN_LIMIT = 1000 # Number of tokens available per story
                   # too few tokens will cut the story at a random spot leaving it unfinished
                   # claude does NOT use more tokens if limit is higher

VOICE_ID = "SAz9YHcvj6GT2YYXdXww"  # voice-id (River)


def _generate_prompt(story_theme,target_lang):
    cultural_content = (
        f"IMPORTANT: Theme of story: {story_theme}"
        if story_theme
        else f"Make the story native to the {target_lang} language (local folklore, metaphores, culture etc)"
    )

    return f"""
    You are a creative writer. Write a short, engaging story in {target_lang}.

    Requirements:
    1. Family-friendly story in {target_lang}.Tone: warm, imaginative, and appropriate for readers of all ages.
    2. Token/word limit: about 300 words, with a complete beginning, middel and end. Do not cut off mid-sentence.
    Very important: Duration:  close to 2 minutes when read out loud (+-5 sec). 
    3. {cultural_content}
    4. Ensure the story has a clear and satisfying ending, and conclude with a complete final sentence before reaching the token limit. Not cutting mid-sentence.
    """


def _generate_story(client, story_theme: str, target_lang: str):
    # Check if the chosen language is supported
    if target_lang not in LANGUAGE_CODES.keys():
        raise ValueError('The chosen language is not supported. ' \
        'Check that the spelling is the same as in the dictionary')
    
    full_prompt = _generate_prompt(story_theme,target_lang)

    response = client.messages.create(
        model = "claude-opus-4-5-20251101",
        max_tokens = TOKEN_LIMIT, # Adjusts the maximum length of the story
        temperature = 1.0, # Range: [0.0,1.0]. Higher temperature generate more varied and less predictable responses
        messages = [
            {"role": "user", "content": full_prompt}
        ]
    )

    return response.content[0].text

def generate_story_and_sound(target_lang: str, story_name: str, story_theme: str = "") -> None:
    """
    Creates an AI-generated story and generates an audiofile of the story.
    The audiofile is stored in same folder as file under folder /Audiofiles generated.
    Ensure the cwd contains a .env file with both anthropic and elevenlabs api-keys.
        Look at CODE_STRUCTURE.md for more information.
    
    Parameters
    ---
    target_lang: str
        language in which to generate the story
    story_name: str
        name of the story, also used as paradigm name
    story_theme: str, default = ""
        theme of the story. If left blank, the story is generated
        native to the language spesified    
    """
    output_dir = Path(__file__).parent / "Audiofiles generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{story_name}.wav"
    load_dotenv()

    # Check to see if the API-key for text-to-speech is added properly before running
    # text generation part of the script to avoid unnecessary calls to the Claude API
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY missing in .env")
    
    # Creates client
    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    story = _generate_story(client, story_theme, target_lang)

    # Text to speech, default = "en"
    language_code = LANGUAGE_CODES.get(target_lang, "en")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=pcm_24000"

    headers = {
        "Accept": "audio/pcm",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": story,
        "model_id": "eleven_multilingual_v2",
        "language_code": language_code,
        "voice_settings": {
            "stability": 0.5, 
            "similarity_boost": 0.75
        }
    }
    # output
    response = requests.post(url, json=data, headers=headers)

    # Create the audiofile if no errors occur, else print error
    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs API failed.\nStatuscode: {response.status_code}\nMessage: {response.text}")
    
    # ElevenLabs returnerer rå PCM-data, ikke en ferdig WAV-fil.
    # Vi oppgir derfor lydformatet og eksporterer som ekte WAV.
    sound = AudioSegment(
        data=response.content,
        sample_width=2,  # PCM er 16-bit
        frame_rate=24000,
        channels=1,
    )

    sound.export(output_path, format="wav") 

    print(f"Lydfil lagret i {output_path}")

if __name__ == "__main__":
    client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    print(_generate_story(client, "","English"))