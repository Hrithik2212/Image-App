import os
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
from groq import Groq

import utils
import entity_extraction
import freshness_classifier

# Initialize FastAPI once
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting origins in production
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

# Set timezone
kolkata_tz = pytz.timezone('Asia/Kolkata')

# Initialize models
classifier_model = freshness_classifier.get_classifier_model()
obj_det_model = YOLO("ml_models/yolov11m_30k_10ep.pt")  # Ensure correct path and model

# Initialize clients
clients = [
    Groq(api_key="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"), 
    Groq(api_key="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"), 
    Groq(api_key="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"), 
]

# Ensure the Data/ directory exists
DATA_DIR = "Data"
os.makedirs(DATA_DIR, exist_ok=True)

@app.post("/upload-image/", summary="Upload an image and receive analysis of detected entities")
async def upload_image(images: List[UploadFile] = File(...)):
    if not images:
        raise HTTPException(status_code=400, detail="No image uploaded")
    
    image = images[0]  # Process the first image in the list

    try:
        # Read the image bytes
        image_bytes = await image.read()
        
        # Open the image using PIL for processing
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image file: {e}")

    try:
        # Perform object detection with YOLO
        # Set IoU threshold to 0.5 for NMS
        # Adjust 'conf' as needed
        res = obj_det_model.predict(
            source=pil_image,
            conf=0.25,  # Confidence threshold
            iou=0.5,    # IoU threshold for NMS
            max_det=20 ,  # Maximum number of detections per image
            agnostic_nms=True
        )
        print(f"Number of detections: {len(res[0])}")
        
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
        print(f"Detections: {detections}")
    except Exception as e:
        logging.error(f"Object Detection Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Object detection failed: {e}")

    analysis_results = []
    try:
        analysis_results = await process_detections_with_clients(
            clients=clients, 
            detections=detections, 
            pil_image=pil_image, 
            image_filename=image.filename
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except AttributeError as ae:
        raise HTTPException(status_code=500, detail=f"Analysis function error: {ae}")
    except Exception as e:
        logging.error(f"Image Analysis Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    # Return the list of analysis results as a JSON response
    return JSONResponse(content=analysis_results)

async def process_detections_with_clients(
    clients: List[Groq],
    detections: List[Dict],
    pil_image: Image.Image,
    image_filename: str
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
            save_path = os.path.join(DATA_DIR, filename)
            cropped_image.save(save_path, format="JPEG")
            print(f"Saved cropped image to {save_path}")

            # Correctly encode the cropped image to bytes
            buffered = io.BytesIO()
            cropped_image.save(buffered, format="JPEG")
            cropped_image_bytes = buffered.getvalue()

            # Convert the cropped image to a base64-encoded URL
            base64_url = utils.image_to_base64_url_bytes(cropped_image_bytes, filename)

            # Call the analyze_image function with the base64 URL and the assigned client
            # Depending on whether analyze_image is async or sync, handle accordingly

            # If analyze_image is asynchronous
            if asyncio.iscoroutinefunction(entity_extraction.analyze_image):
                analysis = await entity_extraction.analyze_image(
                    base64_image_url=base64_url,
                    client=client
                )
            else:
                # If analyze_image is synchronous, run it in a separate thread
                analysis = await asyncio.to_thread(
                    entity_extraction.analyze_image,
                    base64_image_url=base64_url,
                    client=client
                )

            print(f"Analysis for {filename}: {analysis}")

            # Append the result including the Base64-encoded image
            analysis_results.append({
                "detection": det,
                "analysis": analysis,
                "saved_filename": filename,
                "base64_image": base64_url  # Add the Base64 image here
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
