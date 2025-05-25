import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import pygame
from openai import OpenAI
import time

pygame.mixer.init()

MAX_CONCURRENT_TTS = 5
PARAGRAPH_SEPARATOR = "\n\n"  # or adapt as needed!

def split_paragraphs(text, seen):
    """Yield new paragraphs, skipping already seen content."""
    paragraphs = [p.strip() for p in text.split(PARAGRAPH_SEPARATOR) if p.strip()]
    for i, p in enumerate(paragraphs):
        if i >= seen:
            yield (i, p)

async def tts_paragraph(client, paragraph, idx):
    response = await asyncio.to_thread(
        client.audio.speech.create,
        model="tts-1", voice="alloy", input=paragraph, response_format="mp3"
    )
    return idx, response.content

async def play_audio(bytes_io, paragraph=None):
    if paragraph:
        print(f"\n\033[92mNow speaking:\033[0m {paragraph}\n")  # Prints the paragraph in green
    pygame.mixer.music.load(io.BytesIO(bytes_io))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

async def watch_and_tts(txt_path):
    client = OpenAI()
    seen = 0
    results = {}
    playing_idx = 0
    tasks = set()
    loop = asyncio.get_event_loop()

    while True:
        # Read accumulative text
        with open(txt_path, encoding="utf-8") as f:
            curr_text = f.read()

        # Launch TTS for new paragraphs        
        for idx, para in split_paragraphs(curr_text, seen):
            if len(tasks) >= MAX_CONCURRENT_TTS:
                break
            task = asyncio.create_task(tts_paragraph(client, para, idx))
            tasks.add(task)
            seen += 1

        # Check for finished TTS and play in order
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for fut in done:
            idx, audio = await fut
            results[idx] = audio

        # Play audio as soon as the earliest not-yet-played idx is ready
        while playing_idx in results:
            # Access curr_text here, after it's been read from the file
            paragraphs = [p.strip() for p in curr_text.split(PARAGRAPH_SEPARATOR) if p.strip()]
            paragraph_to_speak = paragraphs[playing_idx] if playing_idx < len(paragraphs) else None

            await play_audio(results[playing_idx], paragraph_to_speak)
            del results[playing_idx]
            playing_idx += 1

        # Stop if stable (end of file, all played)
        if not tasks and all(idx < seen for idx in results.keys()):
            await asyncio.sleep(0.5)
            # See if file's grown; else break (or add a CLI arg for "tail mode")
            with open(txt_path, encoding="utf-8") as f:
                if f.read() == curr_text:
                    break
        else:
            await asyncio.sleep(0.5)

def main():
    if len(sys.argv) < 2:
        print("Usage: tts_and_play.py <pdf_path>.txt")
        sys.exit(1)
    txt_path = sys.argv[1]
    asyncio.run(watch_and_tts(txt_path))

if __name__ == "__main__":
    main()