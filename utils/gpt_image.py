from openai import OpenAI
import os
import base64
from pathlib import Path
from utils.config import OPEN_AI_API_KEY
# ─── Configuration ────────────────────────────────────────────────────────────

# Initialize the OpenAI client (reads OPENAI_API_KEY from env)
client = OpenAI(api_key=OPEN_AI_API_KEY)

def generate_and_save_image(
    prompt: str,
    save_dir: str = "~/Desktop/Experiment/MCP",
    model: str = "gpt-image-1",
    quality: str = "medium",
    size: str = "1536x1024"
) -> str:
    """
    Generates an image using the GPT Image 1 API and saves it locally.

    Args:
        prompt: The text prompt to generate the image.
        save_dir: Directory where the image will be stored.
        model: The image generation model identifier.

    Returns:
        The path to the saved image file.
    """
    # Prepare the output directory
    out_path = Path(save_dir).expanduser()
    out_path.mkdir(parents=True, exist_ok=True)

    # Call the image generation endpoint
    result = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        quality=quality,
        size=size
    )

    # Extract Base64-encoded image data
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    # Build a unique filename
    filename = f"gpt_image_{int(Path().stat().st_mtime)}.png"
    file_path = out_path / filename

    # Write the image file
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return str(file_path)


if __name__ == "__main__":
    prompt_text = (
        "A children's book drawing of a veterinarian using a stethoscope to "
        "listen to the heartbeat of a baby otter."
    )
    saved_path = generate_and_save_image(prompt_text)
    print(f"Image saved at: {saved_path}")
