import pydub as pydub
from pathlib import Path
import warnings

def splitAudio(
        name: str,
        nBlocks: int = 6,
        blockLen: int = 20_000
) -> None:
    """
    Resamples the audiofile and splits it into a spesified number of blocks,
    reversing every split and saving every audiofile in the paradigm folder
    under /Audio.

    Parameters
    ---
    name: str
        name of the story
    nBlocks: int, default=6
        number of blocks in which to split the audiofile
    blockLen: int, default=20_000
        length of each block in milliseconds    
    """
    BASE_DIR = Path(__file__).parent
    fileName = f"{name}.wav"

    if " " in name:
        warnings.warn(
            "Story name cannot contain space. Whitespace is being removed.",
            UserWarning)
        
        name = name.replace(" ", "")

    paradigmName = f"Pediatric StoryListening_{name}"

    inputPath = BASE_DIR / "Audiofiles generated" / fileName
    outputPath = BASE_DIR / paradigmName / "audio"

    # Creates folder if non-existent
    outputPath.mkdir(parents=True, exist_ok=True)

    if not inputPath.exists():
        raise FileNotFoundError(f"Did not fint sound file here: {inputPath}")

    sound = pydub.AudioSegment.from_file(inputPath)

    soundLen = len(sound) # ms
    wantedLen = blockLen * nBlocks # ms

    speedFactor = soundLen / wantedLen

    sound_altered = sound._spawn(sound.raw_data, overrides = {
        "frame_rate": int(sound.frame_rate * speedFactor)
    })

    sound = sound_altered.set_frame_rate(sound.frame_rate)
    sound.export(outputPath / "altered_sound.wav", format= "wav")

    for i in range(nBlocks):
        blockStart = i * blockLen
        blockEnd = blockStart + blockLen
        if i == nBlocks:
            blockEnd = soundLen
        block = sound[blockStart:blockEnd]
        reverseBlock = block.reverse()

        block.export(outputPath / f"{name}-{i+1}.wav", format="wav")
        reverseBlock.export(outputPath / f"{name}-{i+1}_backwards.wav", format="wav")


if __name__ == "__main__":
    fileName = "BaselineTest" # original filename
    
    splitAudio(fileName)



