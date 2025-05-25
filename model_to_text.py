import sys
import os
import argparse
from pathlib import Path
from openai import OpenAI


SYSTEM_PROMPT = """
You are a document transcription assistant. 
When given a document or transcript extraction request, return only the text extracted from the document, formatted for text to speech. 
Do not add any introduction, explanation or commentary (such as ```, 'Certainly', 'Here is', or '---'). 
The text will be passed to the OpenAI text-to-speech model, so it should be clean and natural for speech synthesis.
Make sure there are are hints for natural speech, such as removing unnecessary line breaks, fixing formatting artifacts, 
and ensuring it reads smoothly.
Leave clear line breaks where appropriate, such as between paragraphs or sections, as these will be used to create pauses in the speech synthesis.
"""

def stream_text_from_model(client, pdf_path, txt_path):
    with open(pdf_path, "rb") as f:
        file_response = client.files.create(
            file=f,
            purpose="assistants"
        )
    completion = client.chat.completions.create(
        model="gpt-4-1",
        stream=True,
        messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please extract all the text from this PDF and format it naturally for text-to-speech conversion. Remove any formatting artifacts, fix line breaks, and ensure it reads smoothly as natural speech. Return only the cleaned text content."
                        },
                        {
                            "type": "file",
                            "file": {
                                "file_id": file_response.id
                            }
                        }
                    ]
                }
            ],
    )
    client.files.delete(file_response.id)
    with open(txt_path, "w", encoding="utf-8") as fout:
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                fout.write(content)
                fout.flush()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    args = parser.parse_args()
    client = OpenAI()
    txt_path = f"{args.pdf_path}.txt"
    stream_text_from_model(client, args.pdf_path, txt_path)
    print(f"Model output saved to: {txt_path}")

if __name__ == "__main__":
    main()