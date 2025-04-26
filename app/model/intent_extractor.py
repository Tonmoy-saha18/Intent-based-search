import requests
import json
import base64


def get_query_intent(query, image_file=None):
    """
    Call the Gemini API to generate content based on the given prompt and optional image.
    """
    # Replace with your Gemini API key
    GEMINI_API_KEY = "AIzaSyA-JC9b8cOY0H7Ayf-rL6MSJhFUl60Ac7Q"
    prompt = (
        f"Rephrase or refine the following search query to better match the user's intent for product search. "
        f"Focus on the key intent and context of the query. "
        f"Ensure the response is clear and under 75 characters. "
        f"Return only the enhanced query in plain text, without special characters, lists, or multiple options.\n\n"
        f"Query: {query}"
    )

    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    # Request headers
    headers = {
        "Content-Type": "application/json"
    }

    # Prepare the payload
    parts = [{"text": prompt}]

    # If an image file is provided, add it to the parts
    if image_file:
        # Convert the image file to base64
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_base64}})

    # Request payload
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for errors
    if response.status_code != 200:
        raise Exception(f"Gemini API request failed with status code {response.status_code}: {response.text}")

    # Parse the response
    response_data = response.json()
    return response_data