from transformers import MBartForConditionalGeneration, MBart50Tokenizer, AutoModelForCausalLM, AutoTokenizer, pipeline
text_model = AutoModelForCausalLM.from_pretrained(text_generation_model_name)

# Create a pipeline for text generation using the selected model
text_generator = pipeline("text-generation", model=text_model, tokenizer=text_tokenizer)

# Function to generate an image using Hugging Face's text-to-image model
def generate_image_from_text(translated_text):
    try:
        print(f"Generating image from translated text: {translated_text}")
        response = requests.post(API_URL, headers=headers, json={"inputs": translated_text})

        # Check if the response is successful
        if response.status_code != 200:
            print(f"Error generating image: {response.text}")
            return None, f"Error generating image: {response.text}"

        # Read and return the generated image
        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))
        print("Image generation completed.")
        return image, None
    except Exception as e:
        print(f"Error during image generation: {e}")
        return None, f"Error during image generation: {e}"

# Function to generate a shorter paragraph based on the translated text
def generate_short_paragraph_from_text(translated_text):
    try:
        print(f"Generating a short paragraph from translated text: {translated_text}")
        paragraph = text_generator(
            translated_text, 
            max_length=80,  # Reduced to 80 tokens
            num_return_sequences=1, 
            temperature=0.6, 
            top_p=0.8,
            truncation=True  # Added truncation to avoid long sequences
        )[0]['generated_text']
        print(f"Paragraph generation completed: {paragraph}")
        return paragraph
    except Exception as e:
        print(f"Error during paragraph generation: {e}")
        return f"Error during paragraph generation: {e}"

# Define the function to translate Tamil text, generate a short paragraph, and create an image
def translate_generate_paragraph_and_image(tamil_text):
    # Step 1: Translate Tamil text to English using mbart-large-50
    try:
        print("Translating Tamil text to English...")
        tokenizer.src_lang = "ta_IN"
        inputs = tokenizer(tamil_text, return_tensors="pt")
        translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"])
        translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        print(f"Translation completed: {translated_text}")
    except Exception as e:
        return f"Error during translation: {e}", "", None, None

    # Step 2: Generate a shorter paragraph based on the translated English text
    paragraph = generate_short_paragraph_from_text(translated_text)
    if "Error" in paragraph:
        return translated_text, paragraph, None, None

    # Step 3: Generate an image using the translated English text
    image, error_message = generate_image_from_text(translated_text)
    if error_message:
        return translated_text, paragraph, None, error_message

    return translated_text, paragraph, image, None

# Gradio interface setup with share=True to make the app public
iface = gr.Interface(
    fn=translate_generate_paragraph_and_image,
    inputs=gr.Textbox(lines=2, placeholder="Enter Tamil text here..."),
    outputs=[gr.Textbox(label="Translated English Text"), 
             gr.Textbox(label="Generated Short Paragraph"),
             gr.Image(label="Generated Image")],
    title="Tamil to English Translation, Short Paragraph Generation, and Image Creation",
    description="Translate Tamil text to English, generate a short paragraph, and create an image using the translated text.",
    
)

# Launch the app with the share option
iface.launch(share=True)
