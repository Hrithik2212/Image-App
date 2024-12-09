import base64
from pathlib import Path


def image_to_base64_url_bytes(image_bytes: bytes, filename: str) -> str:
    """
    Convert image bytes and filename to a base64 data URL string.
    
    Args:
        image_bytes (bytes): The byte content of the image.
        filename (str): The original filename of the image.
        
    Returns:
        str: The base64-encoded data URL of the image.
    
    Raises:
        ValueError: If the file extension is unsupported.
    """
    # Get the file extension
    extension = Path(filename).suffix.lower()
    
    # Map extensions to MIME types
    mime_type_mapping = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    
    mime_type = mime_type_mapping.get(extension)
    if not mime_type:
        raise ValueError(f"Unsupported file extension: {extension}")
    
    # Encode image bytes to base64
    try:
        encoded_string = base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error encoding image to base64: {e}")
    
    # Create the data URL
    base64_url = f"data:{mime_type};base64,{encoded_string}"
    
    return base64_url