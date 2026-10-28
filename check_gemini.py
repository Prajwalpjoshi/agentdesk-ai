
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

print("Checking available models...\n")

try:
    available = []

    for model in client.models.list():
        actions = model.supported_actions or []
        if "generateContent" in actions:
            name = model.name.replace("models/", "")
            available.append(name)
            print(name)

    preferred = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3-flash-preview",
    ]

    selected = next(
        (name for name in preferred if name in available),
        None,
    )

    if not selected:
        print("\nNo preferred model found. Choose a suitable model above.")
        raise SystemExit(1)

    print(f"\nTesting model: {selected}")

    response = client.models.generate_content(
        model=selected,
        contents="Reply with exactly: AgentDesk connection successful",
    )

    print("Response:", response.text)
    print(f"\nUpdate GEMINI_MODEL={selected} in your .env file.")

except Exception as exc:
    print(f"Model check failed: {type(exc).__name__}: {exc}")
