import base64
import os
from pydantic import BaseModel
import pytz
import asyncio
import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
from ultralytics import YOLO
from dotenv import load_dotenv
import utils
import entity_extraction
import freshness_classifier
from openai import OpenAI
import mysql.connector
import re
from datetime import datetime, timedelta


# Initialize FastAPI once
app = FastAPI()
load_dotenv()

class ImageData(BaseModel):
    images: List[str] 
class SingleImage(BaseModel):
    image : str 

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting origins in production
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)
classifier_model = freshness_classifier.get_classifier_model()
obj_det_model = YOLO("ml_models/yolov11m_30k_10ep.pt")  # Ensure correct path and model
DATA_DIR = "Data"

try:
    connection = mysql.connector.connect(
            host=os.getenv("db_host"),  
            user=os.getenv("db_user"),     
            password=os.getenv("db_password"),
            database='flipkart'  
        )
    if connection.is_connected():
            print("Connected to AWS RDS")
except Exception as e:
        print(f"Error: {e}")

# Set timezone
kolkata_tz = pytz.timezone('Asia/Kolkata')

def insert_into_product_analysis(data):
    keys = [
        "brand_name", "brand_details", "pack_size", "expiry_date",
        "mrp", "product_name", "item_count", "category", "estimated_shelf_life_days"
    ]
    values = tuple(data.get(key, None) for key in keys)
    query = """
    INSERT INTO ProductAnalysis 
    (brand_name, brand_details, pack_size, expiry_date, mrp, product_name, item_count, category, estimated_shelf_life_days)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = connection.cursor()
    cursor.execute(query, values)
    connection.commit()
    print("Inserted into ProductAnalysis")


def parse_date_or_days(input_text):
    if not input_text:
        return None
    if re.match(r"^(0[1-9]|1[0-2])/\d{4}$", input_text):
        return input_text  
    match = re.search(r"(\d+)\s*days?", input_text, re.IGNORECASE)
    if not match:
        match = re.search(r"^\d+$", input_text)
    
    if match:
        days_to_add = int(match.group(1))
        current_date = datetime.now()
        new_date = current_date + timedelta(days=days_to_add)
        return new_date.strftime("%m/%Y")
    
    return None


## NOTE : uncomment first three lines and commnet until the first exception block 

@app.post("/analyze_group/")
async def analyze_group(b64_image:SingleImage):
    header, encoded = b64_image.image.split(",", 1)
    image_data = base64.b64decode(encoded)
    pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')

# async def analyze_image(images: List[UploadFile] = File(...)):
#     if not images:
#         raise HTTPException(status_code=400, detail="No image uploaded")
    
#     image = images[0]  # Process the first image in the list

#     try:
#         # Read the image bytes
#         image_bytes = await image.read()
        
#         # Open the image using PIL for processing
#         pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Failed to read image file: {e}")


    try:
        res = obj_det_model.predict(
            source=pil_image,
            conf=0.25,  # Confidence threshold
            iou=0.5,    # IoU threshold for NMS
            max_det=20 ,  # Maximum number of detections per image
            agnostic_nms=True
        )
        logging.debug(f"Number of detections: {len(res[0])}")
        
        # Extract detections using your custom method
        detections = []
        for box in res[0].boxes:
            xyxy = box.xyxy[0].cpu().numpy()  # Bounding box coordinates
            conf = box.conf[0].cpu().numpy()  # Confidence score
            class_id = int(box.cls[0])
            class_name = obj_det_model.names[class_id]
            # Detection format: [xmin, ymin, width, height]
            x1, y1, x2, y2 = xyxy
            w = x2 - x1
            h = y2 - y1
            detections.append({
                "bbox": [int(x1), int(y1), int(w), int(h)],
                "confidence": float(conf),
                "class_id": class_id,
                "class_name": class_name
            })
        logging.debug(f"Detections: {detections}")
    except Exception as e:
        logging.error(f"Object Detection Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Object detection failed: {e}")

    analysis_results = []
    try:
        analysis_results = await process_detections_with_clients(
            clients=[OpenAI(api_key=os.getenv("OPENAI_API_KEY")) for _ in range(len(detections))], 
            detections=detections, 
            pil_image=pil_image, 
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except AttributeError as ae:
        raise HTTPException(status_code=500, detail=f"Analysis function error: {ae}")
    except Exception as e:
        logging.error(f"Image Analysis Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    # Return the list of analysis results as a JSON response
    print("data",analysis_results)
    for i in analysis_results:
        if "expiry_date" in i:
            i["expiry_date"]=parse_date_or_days(i["expiry_date"])
        insert_into_product_analysis(i)
    return JSONResponse(content=analysis_results)



## NOTE : uncomment the till base64 part and comment till finallty block
@app.post("/multi_image_ocr/", summary="Upload images and process them")
async def upload_image(data: ImageData):
    base64_images = []
    for index, image_base64 in enumerate(data.images):
        base64_images.append(image_base64)
# async def upload_images(files: List[UploadFile]= File(...)): #->Dict :
#     base64_images = []
#     for file in files:
#         # Validate the file type (optional but recommended)
#         if not file.content_type.startswith("image/"):
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Invalid file type: {file.filename}. Only image files are allowed."
#             )
        
#         try:
#             # Read the file content
#             contents = await file.read()
#             image = Image.open(io.BytesIO(contents))
#             image.verify()  # This will raise an exception if the image is not valid
#             base64_str = base64.b64encode(contents).decode('utf-8')
#             base64_images.append(base64_str)
#         except Exception as e:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Failed to process file {file.filename}: {str(e)}"
#             )
#         finally:
#             await file.close()
    data= entity_extraction.ocr_mulitple_images(base64_images , OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    if "expiry_date" in data:
            data["expiry_date"]=parse_date_or_days(data["expiry_date"])
    insert_into_product_analysis(data)
    return data
    


async def process_detections_with_clients(
    clients: List[OpenAI],
    detections: List[Dict],
    pil_image: Image.Image,
) -> List[Dict]:

    analysis_results = []
    client_queue = asyncio.Queue()

    # Populate the queue with clients
    for client in clients:
        await client_queue.put(client)

    # Use enumerate to assign sequential numbers starting from 1
    async def analyze_detection(det: Dict, index: int) -> None:
        nonlocal analysis_results
        client = await client_queue.get()
        try:
            x, y, w, h = det["bbox"]
            class_id = det['class_id']
            conf = det['confidence']
            class_name = det['class_name']
            # Ensure bounding box is within image bounds
            img_width, img_height = pil_image.size
            x = max(0, x)
            y = max(0, y)
            w = min(w, img_width - x)
            h = min(h, img_height - y)

            # Crop the image using PIL
            cropped_image = pil_image.crop((x, y, x + w, y + h))

            # Save cropped image to Data/ directory with sequential filename
            filename = f"{index}.jpg"
            # save_path = os.path.join(DATA_DIR, filename)
            # cropped_image.save(save_path, format="JPEG")
            # logging.debug(f"Saved cropped image to {save_path}")

            # Correctly encode the cropped image to bytes
            buffered = io.BytesIO()
            cropped_image.save(buffered, format="JPEG")
            cropped_image_bytes = buffered.getvalue()

            # Convert the cropped image to a base64-encoded URL
            base64_url = utils.image_to_base64_url_bytes(cropped_image_bytes, filename)

            # Call the perform_ocr_extraction function with the base64 URL and the assigned client
            # Depending on whether perform_ocr_extraction is async or sync, handle accordingly

            # If perform_ocr_extraction is asynchronous
            if class_id == 0:
            # Call perishable_analyze
            # Assuming perishable_analyze is synchronous
                if asyncio.iscoroutinefunction(entity_extraction.perishable_analyze):
                    analysis = await entity_extraction.perishable_analyze(
                        base64_image=base64_url,
                        client=client,
                        classifier_model=classifier_model,
                        device=freshness_classifier.device,
                        threshold=0.9
                    )
                    # logging.debug(analysis.keys())
                    if not analysis['product_name'] : 
                        analysis = analysis = await asyncio.to_thread(
                        entity_extraction.perform_ocr_extraction,
                        base64_image=base64_url,
                        openai_client=client)

                else:
                    # Run perishable_analyze in a separate thread if it's synchronous
                    analysis = await asyncio.to_thread(
                        entity_extraction.perishable_analyze,
                        base64_image=base64_url,
                        client=client,
                        classifier_model=classifier_model,
                        device=freshness_classifier.device,
                        threshold=0.9
                    )
                    if not analysis['product_name'] : 
                        analysis  = await asyncio.to_thread(
                        entity_extraction.perform_ocr_extraction,
                        base64_image=base64_url,
                        openai_client=client)
            elif class_id == 1:
                # Call perform_ocr_extraction
                if asyncio.iscoroutinefunction(entity_extraction.perform_ocr_extraction):
                    analysis = await entity_extraction.perform_ocr_extraction(
                        base64_image=base64_url,
                        client=client
                    )
                else:
                    # Run perform_ocr_extraction in a separate thread if it's synchronous
                    analysis = await asyncio.to_thread(
                        entity_extraction.perform_ocr_extraction,
                        base64_image=base64_url,
                        openai_client=client
                    )
            else:
                # Handle unexpected class_id values if necessary
                raise ValueError(f"Unsupported class_id: {class_id}")

#            logging.debug(f"Analysis for {filename}: {analysis}")

            # Append the result including the Base64-encoded image
            analysis_results.append({
                "base64_image": base64_url , 
                  **analysis  # Add the Base64 image here
            })

        except Exception as e:
            logging.error(f"Error processing detection {det}: {e}", exc_info=True)
            analysis_results.append({
                "detection": det,
                "analysis": None,
                "error": str(e),
                "saved_filename": filename if 'filename' in locals() else None,
                "base64_image": None
            })
        finally:
            # Put the client back into the queue
            await client_queue.put(client)

    # Create a list of tasks with enumeration for sequential filenames
    tasks = [
        asyncio.create_task(analyze_detection(det, index))
        for index, det in enumerate(detections, start=1)
    ]

    # Await all tasks to complete
    await asyncio.gather(*tasks)

    return analysis_results
