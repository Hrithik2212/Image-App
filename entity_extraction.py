from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os 
import base64
from freshness_classifier import classify_image , device
from typing import Optional , Dict , Any 
from PIL import Image 
import io 

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the ProductAnalysis model
class ProductAnalysis(BaseModel):
    brand_name: Optional[str] = Field(None, description="Name of the brand")
    brand_details: Optional[str] = Field(None, description="Details about the brand, such as logo or tagline")
    pack_size: Optional[str] = Field(None, description="Size of the product pack")
    expiry_date: Optional[str] = Field(None, description="Expiry date of the product")
    mrp: Optional[str] = Field(None, description="Maximum Retail Price of the product")
    product_name: Optional[str] = Field(None, description="Name of the product")
    item_count: Optional[int] = Field(None, description="Number of items in the image")
    category: Optional[str] = Field(None, description="Category of the product, e.g., personal care, household items")

class FreshnessAnalysis(BaseModel):
    product_name: Optional[str] = Field(
        None, 
        description="Name of the product (e.g., apple, banana, bread, etc.)"
    )
    item_count: Optional[int] = Field(
        None, 
        description="Count/quantity of items present in the image"
    )
    category: Optional[str] = Field(
        None, 
        description="Category of the product (e.g., fruit, vegetable, bread)"
    )
    estimated_shelf_life_days: Optional[int] = Field(
        None, 
        description="Estimated shelf life in terms of days"
    )


def perform_ocr_extraction(base64_image: str, openai_client: OpenAI) -> Dict:
    prompt = """
Analyze the image of a grocery product and extract the following information: 
- Brand name
- Brand details (e.g., logo/tagline)
- Pack size
- Expiry date
- MRP (Maximum Retail Price)
- Product name
- Count/quantity of items - count of the product present in the image 
- Category of the product (e.g., personal care, household items, health supplements, etc.)
"""

    try:
        # Prepare the messages with text and image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{base64_image}" 
                        }
                    }
                ]
            }
        ]

        # Make the API call
        completion = openai_client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=ProductAnalysis,
            temperature=0
        )

        # Extract the parsed message
        result = completion.choices[0].message.parsed

        return result.model_dump()

    except Exception as e:
        print(f"An error occurred during OCR extraction: {e}")
        return None


def analyze_freshness(base64_image: str, openai_client: OpenAI) -> Dict:
    prompt = """
Analyze the image of a grocery product and extract the following information:
- Name of the product (e.g., apple, banana, bread, etc.)
- Count/quantity of items - count of the identified product present in the image (eg - 1,2 ...)
- Category of the product (e.g., fruit, vegetable, bread)
- Estimated shelf life (in terms of days)

Edge Case 
If in case the fruit seems spoiled then the estimated shelf life is 0
"""
    try:
        # Prepare the messages with text and image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}" 
                        }
                    }
                ]
            }
        ]

        # Make the API call
        completion = openai_client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=FreshnessAnalysis,
            temperature=0
        )
        result = completion.choices[0].message.parsed
        print(result)
        return result.model_dump()

    except Exception as e:
        print(f"An error occurred during OCR extraction: {e}")
        return None


def perishable_analyze(
    base64_image: str,
    client: Any,
    classifier_model: Any,
    device: Optional[Any] = None,
    threshold: float = 0.9
) -> Dict[str, Any]:
    # Step 1: Decode the Base64 image
    try:
        # If the Base64 string includes the data URL prefix, remove it
        if base64_image.startswith('data:'):
            header, encoded = base64_image.split(',', 1)
        else:
            encoded = base64_image

        image_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
    except Exception as e:
        return {"error": f"Failed to decode or open image: {str(e)}"}

    # Step 2: Classify the image
    try:
        predicted_label, probability = classify_image(
            image,
            classifier_model,
            device=device,
            threshold=threshold
        )
    except Exception as e:
        return {"error": f"Image classification failed: {str(e)}"}

    # Step 3: Analyze the image using the freshness analysis API
    try:
        analysis_result = analyze_freshness(encoded , client)
        if 'error' in analysis_result:
            return analysis_result  # Return the error from analyze_freshness
    except Exception as e:
        return {"error": f"Freshness analysis failed: {str(e)}"}

    # Step 4: Combine the results
    try:
        result = {
            "image" : encoded , 
            "product_name": analysis_result.get("product_name", None),
            "count": analysis_result.get("item_count", None),
            "category": analysis_result.get("category", None),
            "estimated_shelf_life_days": analysis_result.get("estimated_shelf_life_days", None),
            "state": predicted_label,             # Classifier model prediction ('fresh' or 'rotten')
            "freshness": (1 - probability)       # Classifier model probability
        }
        return result
    except Exception as e:
        return {"error": f"Failed to combine results: {str(e)}"}


# Example usage
if __name__ == "__main__":
    def encode_image(image_path: str) -> str:
        """Encode an image file to a Base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # # Path to your image
    # image_path = "Data/1.jpg"

    # # Encode the image to Base64
    # base64_image = encode_image(image_path)

    # # Perform OCR extraction
    # product_info = perform_ocr_extraction(base64_image, client)

    # # Print the extracted information
    # if product_info:
    #     print(product_info.model_dump())
    # else:
    #     print("No information extracted.")
    from freshness_classifier import get_classifier_model
    model = get_classifier_model() 

    image_path ="Data/rotten-apple.webp"
    base64_image = encode_image(image_path)

    print(perishable_analyze(base64_image , client , model , device))

def ocr_mulitple_images(b64_images , openai_client)-> Dict:
    prompt = """
Following are the images of a single grocery product from different angles 
Analyze the images of the given grocery product and extract the following information: 
- Brand name
- Brand details (e.g., logo/tagline)
- Pack size
- Expiry date
- MRP (Maximum Retail Price)
- Product name
- Count/quantity of items - count of the product present in the image 
- Category of the product (e.g., personal care, household items, health supplements, etc.)
"""

    try:
        # Prepare the messages with text and image
        content = [
            {"type": "text","text": prompt}
            ]
        content.extend([{"type": "image_url" , "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}} for b64_image in b64_images])
        messages = [
            {
                "role": "user",
                "content": content
            }
        ]

        # Make the API call
        completion = openai_client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=ProductAnalysis,
            temperature=0
        )

        # Extract the parsed message
        result = completion.choices[0].message.parsed

        return result.model_dump()

    except Exception as e:
        print(f"An error occurred during OCR extraction: {e}")
        return None
