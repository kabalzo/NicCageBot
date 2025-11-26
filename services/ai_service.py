import os
import logging
from openai import OpenAI
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import discord

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"
        self.image_model = "dall-e-3"

    async def ask_question(self, prompt):
        try:
            logger.info(f"Gemini processing question: {prompt[:100]}...")  # Log first 100 chars
            full_prompt = "You are Nicolas Cage the famous actor. Keep responses somewhat succinct, but still with flair. " + prompt

            logger.info("Sending request to Gemini API...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )

            # Add detailed logging
            response_text = response.text
            logger.info(f"Gemini response received ({len(response_text)} characters)")
            logger.info(f"Response preview: {response_text[:200]}...")  # First 200 chars

            return response_text

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise    
    
    async def create_image(self, prompt):
        response = self.client.images.generate(
            model=self.image_model,
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
            style="natural"
        )
        return response.data[0].url

class GeminiService:
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            logger.info(f"Checking for Gemini API key...")

            if not api_key:
                logger.error("ERROR: GEMINI_API_KEY not found in environment variables")
                raise ValueError("GEMINI_API_KEY not set")
            else:
                logger.info("Gemini API key found")

            logger.info("Initializing Gemini client...")
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.0-flash"
            self.image_model = "imagen-3.0-generate-002"
            logger.info("Gemini service initialized successfully")

        except Exception as e:
            logger.error(f"Gemini service initialization failed: {e}")
            raise
    
    async def ask_question(self, prompt):
        try:
            logger.info(f"Gemini processing question: {prompt[:100]}...")  # Log first 100 chars
            full_prompt = "You are Nicolas Cage the famous actor. Keep responses somewhat succinct, but still with flair. " + prompt

            logger.info("Sending request to Gemini API...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )

            # Add detailed logging
            response_text = response.text
            logger.info(f"Gemini response received ({len(response_text)} characters)")
            logger.info(f"Response preview: {response_text[:200]}...")  # First 200 chars

            return response_text

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

    # === ADD THIS METHOD ===
    async def create_images(self, prompt):
        try:
            logger.info(f"Gemini processing image prompt: {prompt}")
            directory = "images"
            names = ["one", "two", "three", "four"]
            images = []
            
            os.makedirs(directory, exist_ok=True)
            
            response = self.client.models.generate_images(
                model=self.image_model,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=4)
            )

            logger.info(f"Gemini generated {len(response.generated_images)} images")

            for name, generated_image in zip(names, response.generated_images):
                file_path = f"{directory}/output_image_{name}.png"
                image = Image.open(BytesIO(generated_image.image.image_bytes))
                image.save(file_path)

                with open(file_path, 'rb') as fp:
                    image_bytes = fp.read()
                    image_io = BytesIO(image_bytes)
                    images.append(discord.File(image_io, filename=os.path.basename(file_path)))

            return images

        except Exception as e:
            logger.error(f"Gemini image creation error: {e}")
            raise
