 def generate_cosmic_pet_image(uploaded_image_path, pet_name=None, species=None, breed=None):
    """
    Sends the uploaded image to Replicate (IP-Adapter + SDXL) and returns the transformed image URL.
    """
    import replicate
    import requests
    import os
    import hashlib

    # Hash the image so we can cache it
    with open(uploaded_image_path, "rb") as f:
        image_bytes = f.read()
        image_hash = hashlib.sha256(image_bytes).hexdigest()

    # Check if this image already exists in cloud (optional logic placeholder)

    # Construct prompt
    prompt = f"Portrait of a {species or 'pet'}"
    if breed:
        prompt += f" ({breed})"
    prompt += " in a cosmic fantasy style, surrounded by stars and glowing light, highly detailed, ethereal, watercolor style."

    negative_prompt = "blurry, low quality, extra limbs, mutated, human, text, watermark, signature, bad anatomy"

    # Send to Replicate
    replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
    version = "replace-this-with-model-version"  # Gemini will fill this in with pinned version hash
    output = replicate_client.run(
        f"tencentarc/ip-adapter-sdxl:{version}",
        input={
            "image": open(uploaded_image_path, "rb"),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_guidance_scale": 1.0,
            "num_outputs": 1
        }
    )

    # Get the output image URL
    output_url = output[0]  # Assuming output is a list

    # Download the result temporarily
    response = requests.get(output_url, stream=True)
    temp_out_path = f"/tmp/{image_hash}_transformed.jpg"
    with open(temp_out_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    # Gemini will now upload this image to cloud (Supabase/S3/Cloudinary) and return final public URL
    final_url = upload_to_cloud_storage(temp_out_path, image_hash)

    return final_url