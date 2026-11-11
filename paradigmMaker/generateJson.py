import json
from pathlib import Path
import copy
import uuid
import time
import warnings

def _set_block_length(content: dict, blockLength: int) -> None:
    content["variables"]["OnBlockLength"] = blockLength
    content["settings"]["averageBlockLength"] = blockLength

def _set_language_and_description(content: dict, language:str) -> None:
    content["languages"] = [language]
    content["settings"]["description"][language] = copy.deepcopy(
        content["settings"]["description"].pop("English")
        )

    if language != "English":
        print(f"\nNote: Description for {language} is in English. It should be translated.\n")
        content["defaults"]["language"] = language

def _timestamp() -> int:
    return int(time.time()*1000)

def _make_slide(
        protocol_slide: dict,
        i: int,
        name: str
    ) -> tuple[dict,dict]:
    slide = copy.deepcopy(protocol_slide)
    reverse_slide = copy.deepcopy(protocol_slide)

    slide["name"] = f"Audio{i+1}"
    reverse_slide["name"] = f"ReverseAudio{i+1}"

    slide["creationDate"] = _timestamp()
    reverse_slide["creationDate"] = _timestamp()

    slide["id"] = str(uuid.uuid4())
    reverse_slide["id"] = str(uuid.uuid4())

    slide["sound"]["value"] = f"./audio/{name}-{i+1}.wav"
    reverse_slide["sound"]["value"] = f"./audio/{name}-{i+1}_backwards.wav"

    return slide, reverse_slide

def _insert_slides(
        content: dict,
        nBlocks: int,
        name: str,
        language: str
    ) -> None:
    for version in content["versions"]:
        version_slides = content["slide"][version]

        protocol_slide = version_slides[1]
        new_slides = version_slides[:1] # keeps only the start-slide

        new_slides[0]["id"] = str(uuid.uuid4())

        for i in range(nBlocks):
            slide, reverse_slide = _make_slide(protocol_slide, i, name)
            new_slides.append(slide)
            new_slides.append(reverse_slide)

        content["slide"][f"{language}-{version}"] = new_slides
        del content["slide"][version]

def _insert_trials(content: dict, nBlocks: int) -> dict[str,str]:
    trial = content["trial"]
    protocol_trial = trial[1]

    # s = start, r1 = reverse 1, a1 = audio1, r2 = reverse 2 ...
    trial_ids = {}

    start_trial = trial[0]
    new_trials = [copy.deepcopy(start_trial)]
    new_trials[0]["id"] = str(uuid.uuid4())
    trial_ids["s"] = new_trials[0]["id"]

    for i in range(nBlocks):
        new_trial = copy.deepcopy(protocol_trial)

        new_trial["name"] = f"Audio{i+1}"
        new_trial["show"][0]["item"] = f"Audio{i+1}"

        trial_id = str(uuid.uuid4())
        trial_ids[f"a{i+1}"] = trial_id
        new_trial["id"] = trial_id

        new_r_trial = copy.deepcopy(protocol_trial)
        new_r_trial["name"] = f"Reverse{i+1}"
        new_r_trial["show"][0]["item"] = f"ReverseAudio{i+1}"

        r_trial_id = str(uuid.uuid4())
        trial_ids[f"r{i+1}"] = r_trial_id
        new_r_trial["id"] = r_trial_id
        new_trials.append(new_r_trial)
        new_trials.append(new_trial)

    # last trial is reverse, same as the first reverse trial
    last_trial = copy.deepcopy(protocol_trial)
    last_trial["name"] = f"Reverse{nBlocks+1}"
    last_trial["show"][0]["item"] = "ReverseAudio1"
    last_trial_id = str(uuid.uuid4())
    last_trial["id"] = last_trial_id
    trial_ids[f"r{nBlocks+1}"] = last_trial_id
    new_trials.append(last_trial)

    content["trial"] = new_trials

    return trial_ids

def _insert_blocks(
        content: dict,
        nBlocks: int,
        trial_ids: dict[str,str]
    ) -> dict[str,str]:
    protocol_block = content["blocks"][0]

    # a1 = active 1, r1 = reverse 1, ...
    block_ids = {}

    new_blocks = []

    for i in range(nBlocks):
        a_block = copy.deepcopy(protocol_block)
        r_block = copy.deepcopy(protocol_block)

        a_block["name"] = f"Story{i+1}"
        a_block["condition"] = 1
        a_block["trials"] = [trial_ids[f"a{i+1}"]]
        a_id = str(uuid.uuid4())
        a_block["id"] = a_id
        block_ids[f"a{i+1}"] = a_id

        r_block["name"] = f"Reverse{i+1}"
        r_block["condition"] = 0
        r_block["trials"] = [trial_ids[f"r{i+1}"]]
        r_id = str(uuid.uuid4())
        r_block["id"] = r_id
        block_ids[f"r{i+1}"] = r_id

        new_blocks.append(r_block)
        new_blocks.append(a_block)

    last_block = copy.deepcopy(protocol_block)
    last_block["name"] = f"Reverse{nBlocks+1}"
    last_block["condition"] = 0
    last_block["trials"] = [trial_ids[f"r{nBlocks+1}"]]
    last_id = str(uuid.uuid4())
    last_block["id"] = last_id
    block_ids[f"r{nBlocks+1}"] = last_id

    new_blocks.append(last_block)

    content["blocks"] = new_blocks

    return block_ids

def _insert_sessions(
        content: dict,
        nBlocks: int,
        trial_ids: dict[str,str],
        block_ids: dict[str,str]
    ) -> None:
    new_session = []

    start = trial_ids["s"]
    new_session.append(start)

    for i in range(nBlocks):
        new_session.append(block_ids[f"r{i+1}"])
        new_session.append(block_ids[f"a{i+1}"])

    new_session.append(block_ids[f"r{nBlocks+1}"])

    content["session"]["run"] = new_session
   
def generate_json(
        language: str,
        storyName: str,
        nBlocks: int = 6,
        blockLength: int = 20_000
) -> None:
    """
    Generates the nordicAktiva-compatible JSON-file containing
    the generated audiofiles.
    The JSON-file is stored in the paradigm folder together with the audiofiles

    Parameters
    ---
    language: str
        language in which the story is generated
    storyName: str
        name of the story, used as the name of the paradigm as well
    nBlocks: int, default=6
        number of blocks in the paradigm
    blockLenth: int, default=20_000
        length of each individual block in milliseconds
    """
    if " " in storyName:
        warnings.warn(
            "Story name cannot contain space. Whitespace is being removed.",
            UserWarning)
        
        storyName = storyName.replace(" ", "")
    
    protocol_path = Path(__file__).parent / "protocol.json"
    data = json.loads(protocol_path.read_text(encoding="utf-8"))

    paradigm_name = f"Pediatric StoryListening_{storyName}"
    data["settings"]["name"] = paradigm_name

    _set_block_length(data,blockLength)
    _set_language_and_description(data, language)
    _insert_slides(data, nBlocks, storyName, language)
    trialId = _insert_trials(data, nBlocks)
    blockId = _insert_blocks(data, nBlocks, trialId)
    _insert_sessions(data, nBlocks, trialId, blockId)

    output_dir = Path(__file__).parent / paradigm_name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{paradigm_name}.json"

    json_string = json.dumps(data, indent=2, ensure_ascii=False)

    output_path.write_text(json_string, encoding="utf-8")

    print(f"Json successfully saved in {output_path}\n")


if __name__ == "__main__":
    generate_json(
        "Swedish",
        "KPop"
    )
