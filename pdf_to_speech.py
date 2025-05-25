#!/usr/bin/env python3
"""
OpenAI PDF to Speech Client
Loads a PDF using OpenAI's API and converts it to natural speech with streaming audio.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path
import pygame
import io
from openai import OpenAI

# Initialize pygame mixer for audio playback
pygame.mixer.init()


def load_pdf_with_openai(client, pdf_path):
    """Load PDF content using OpenAI's file upload and processing capability."""
    try:
        # Upload the PDF file
        with open(pdf_path, "rb") as f:
            file_response = client.files.create(
                file=f,
                purpose="assistants"
            )

        # Create a message to extract text from the PDF
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated to use gpt-4o instead of gpt-4.1
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please extract all the text from this PDF and format it naturally for text-to-speech conversion. Remove any formatting artifacts, fix line breaks, and ensure it reads smoothly as natural speech. Return only the cleaned text content."
                        },
                        {
                            "type": "file",
                            "file": {  # Changed from "file_id" to nested "file" object
                                "file_id": file_response.id
                            }
                        }
                    ]
                }
            ]
        )

        # Clean up the uploaded file
        client.files.delete(file_response.id)

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None


def save_text_file(text_content, pdf_path):
    """Save the processed text as a .pdf.txt file."""
    txt_path = f"{pdf_path}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    print(f"Saved processed text to: {txt_path}")
    return txt_path


async def text_to_speech_streaming(client, text_content, pdf_path):
    """Convert text to speech with streaming audio playback."""
    try:
        # Split text into chunks for streaming
        chunk_size = 1000  # Adjust based on needs
        text_chunks = [text_content[i:i + chunk_size] for i in range(0, len(text_content), chunk_size)]

        audio_path = f"{pdf_path}.mp3"
        audio_chunks = []

        print("Converting to speech and playing...")

        for i, chunk in enumerate(text_chunks):
            if not chunk.strip():
                continue

            print(f"Processing chunk {i + 1}/{len(text_chunks)}")

            # Generate speech for this chunk
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=chunk,
                response_format="mp3"
            )

            # Get audio data
            audio_data = response.content
            audio_chunks.append(audio_data)

            # Play audio immediately
            pygame.mixer.music.load(io.BytesIO(audio_data))
            pygame.mixer.music.play()

            # Wait for this chunk to finish before starting the next
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

        # Save complete audio file
        with open(audio_path, 'wb') as f:
            for chunk in audio_chunks:
                f.write(chunk)

        print(f"Saved complete audio to: {audio_path}")

    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Convert PDF to speech using OpenAI")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI()  # Uses OPENAI_API_KEY environment variable

    print(f"Loading PDF: {pdf_path}")

    # Extract text from PDF
    text_content = load_pdf_with_openai(client, str(pdf_path))
    if not text_content:
        print("Failed to extract text from PDF")
        sys.exit(1)

    print("PDF text extracted successfully")

    # Save processed text
    save_text_file(text_content, str(pdf_path))

    # Convert to speech and play
    await text_to_speech_streaming(client, text_content, str(pdf_path))

    print("Conversion complete!")


if __name__ == "__main__":
    asyncio.run(main())