from minio import Minio
from PIL import Image, ImageDraw, ImageFont  # NAYA: Draw aur Font libraries
import io
import requests
import datetime
import pytesseract
import os  # NAYA: File ka naam change karne ke liye

# Tesseract ka rasta
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def main(args):
    client = Minio(
        "localhost:9000", 
        access_key="admin",
        secret_key="password123",
        secure=False
    )

    bucket_name = args.get("bucket", "uploads")
    object_name = args.get("key", "test.jpg")
    
    response = None
    try:
        response = client.get_object(bucket_name, object_name)
        image_data = response.read()
        
        # 1. Image open karna
        img = Image.open(io.BytesIO(image_data))
        original_width, original_height = img.size 
        
        # 2. OCR Text Extract karna
        extracted_text = pytesseract.image_to_string(img).strip()
        if not extracted_text:
            extracted_text = "Koi text nahi mila"
            
        # 3. Thumbnail banana
        img.thumbnail((300, 300))
        
        # ----------------------------------------------------
        # NAYA HISSA 1: WATERMARK OVERLAY
        # ----------------------------------------------------
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default() # Default font use kar rahe hain
        watermark_text = "Group 18"
        
        # Text ko bottom-right par lagana (safaid text, kaalay border ke sath)
        width, height = img.size
        # Andaazan text ki jagah calculate ki hai
        position = (width - 60, height - 15) 
        draw.text(position, watermark_text, fill="white", font=font, stroke_width=1, stroke_fill="black")
        # ----------------------------------------------------
        
        # ----------------------------------------------------
        # NAYA HISSA 2: FORMAT CONVERSION (WEBP)
        # ----------------------------------------------------
        # Purane naam se .jpg/.png hatana aur aakhir mein .webp lagana
        base_name = os.path.splitext(object_name)[0]
        new_object_name = "thumb_" + base_name + ".webp"
        
        img_byte_arr = io.BytesIO()
        # Save karte waqt format WEBP kar diya
        img.save(img_byte_arr, format="WEBP")
        img_byte_arr.seek(0)
        # ----------------------------------------------------
        
        # 4. Nayi WEBP image upload karna
        client.put_object(
            "processed", 
            new_object_name, 
            img_byte_arr, 
            length=img_byte_arr.getbuffer().nbytes
        )

        # 5. Database mein final record save karna
        db_url = "http://admin:password123@localhost:5984/image_metadata"
        metadata_record = {
            "original_image_name": object_name,
            "processed_image_name": new_object_name,
            "original_size": f"{original_width}x{original_height}",
            "extracted_text": extracted_text,
            "status": "Thumbnail, OCR, Watermark & WebP Completed!",
            "time_processed": str(datetime.datetime.now())
        }
        
        requests.post(db_url, json=metadata_record)
        
        return {
            "status": "Success", 
            "message": f"Project Complete! {new_object_name} ban gayi hai."
        }
        
    except Exception as e:
        return {"status": "Error", "message": str(e)}
    finally:
        if response:
            response.close()
            response.release_conn()

if __name__ == "__main__":
    print(main({"bucket": "uploads", "key": "test.jpg"}))