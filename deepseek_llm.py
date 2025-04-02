import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables (or set directly for testing)
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API")  # Replace with your API key if not in .env

# Initialize the OpenAI client with DeepSeek's endpoint
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"  # DeepSeek's custom endpoint
)

def test_deepseek_non_streaming():
    """Test DeepSeek API in non-streaming mode."""
    logger.info("Testing DeepSeek API in non-streaming mode...")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # Use the appropriate model name for DeepSeek
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you today?"}
            ],
            stream=False  # Non-streaming mode
        )
        
        # Extract and print the response
        if response.choices and len(response.choices) > 0:
            ai_response = response.choices[0].message.content
            logger.info(f"Non-streaming response: {ai_response}")
        else:
            logger.warning("No response choices found in non-streaming mode.")

    except Exception as e:
        logger.error(f"Error in non-streaming test: {str(e)}")

def test_deepseek_streaming():
    """Test DeepSeek API in streaming mode."""
    logger.info("Testing DeepSeek API in streaming mode...")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a short story about a robot."}
            ],
            stream=True  # Streaming mode
        )
        
        # Process and print the streaming response
        full_response = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)  # Real-time printing
        
        # print("\nFinal streaming response: " + full_response)
        logger.info("Streaming test completed successfully.")

    except Exception as e:
        logger.error(f"Error in streaming test: {str(e)}")

def main():
    """Run both tests."""
    # test_deepseek_non_streaming()
    # print("\n" + "-"*50 + "\n")
    test_deepseek_streaming()

if __name__ == "__main__":
    main()