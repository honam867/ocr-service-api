#!/usr/bin/env python3
# coding: utf-8
# @2022-04-19 20:52:24
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:

from flask import Flask, request, jsonify, make_response
import os
import time
import tempfile
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF for PDF processing
from paddleocr import PaddleOCR
from PIL import Image
import io
import base64
import json
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ensure all responses have proper JSON content type
@app.after_request
def after_request(response):
    # Set Content-Type to JSON for all responses since this is a JSON API
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    # Add CORS headers if needed
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = 'temp_uploads'

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize PaddleOCR instances lazily to avoid duplicate initialization in debug mode
ocr_en = None
ocr_vi = None

def get_ocr_instance(language='en'):
    """Get or initialize OCR instance for the specified language"""
    global ocr_en, ocr_vi
    
    try:
        if language == 'en' and ocr_en is None:
            logger.info("Initializing PaddleOCR for English...")
            ocr_en = PaddleOCR(
                lang='en',
                use_angle_cls=True,
                use_gpu=False
            )
            logger.info("PaddleOCR English instance initialized successfully")
        elif language == 'vi' and ocr_vi is None:
            logger.info("Initializing PaddleOCR for Vietnamese...")
            ocr_vi = PaddleOCR(
                lang='vi',
                use_angle_cls=True,
                use_gpu=False
            )
            logger.info("PaddleOCR Vietnamese instance initialized successfully")
        
        return ocr_en if language == 'en' else ocr_vi
        
    except Exception as e:
        logger.error(f"Failed to initialize PaddleOCR for {language}: {e}")
        raise

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_images(pdf_path):
    """Convert PDF pages to images"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Convert page to image with high resolution
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Convert to PIL Image
        img = Image.open(io.BytesIO(img_data))
        images.append({
            'page': page_num + 1,
            'image': img
        })
    
    doc.close()
    return images

def perform_ocr(images, language='en'):
    """Perform OCR on images with specified language"""
    ocr_instance = get_ocr_instance(language)
    results = []
    
    for img_data in images:
        page_num = img_data['page']
        img = img_data['image']
        
        # Convert PIL Image to numpy array for PaddleOCR
        img_np = np.array(img.convert('RGB'))
        
        try:
            # Perform OCR on the numpy array
            result = ocr_instance.ocr(img_np)
            
            # Extract text from result
            page_text = ""
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                        page_text += text + "\n"
            
            results.append({
                'page': page_num,
                'text': page_text.strip(),
                'line_count': len(page_text.strip().split('\n'))
            })
            
        except Exception as e:
            logger.error(f"OCR failed for page {page_num}: {e}")
            results.append({
                'page': page_num,
                'text': "",
                'line_count': 0,
                'error': str(e)
            })
    
    return results

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'service': 'OCR API Service',
        'status': 'running',
        'supported_languages': ['en', 'vi'],
        'supported_formats': ['pdf'],
        'version': '1.0.1',
        'endpoints': {
            'extract_text': '/extract-text (POST)',
            'health': '/ (GET)'
        }
    })

@app.route('/extract-text', methods=['POST'])
def extract_text():
    """Extract text from uploaded PDF file"""
    start_time = time.time()
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            response = jsonify({
                'error': 'No file provided',
                'message': 'Please upload a PDF file using the "file" parameter'
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            response = jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        # Check file extension
        if not allowed_file(file.filename):
            response = jsonify({
                'error': 'Invalid file format',
                'message': 'Only PDF files are supported'
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        # Get language parameter (default to 'en')
        language = request.form.get('language', 'en').lower()
        if language not in ['en', 'vi']:
            response = jsonify({
                'error': 'Unsupported language',
                'message': 'Supported languages: en, vi'
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_filepath)
        
        try:
            # Convert PDF to images
            logger.info(f"Processing PDF: {temp_filename}")
            images = pdf_to_images(temp_filepath)
            
            if not images:
                response = jsonify({
                    'error': 'PDF processing failed',
                    'message': 'Could not extract pages from PDF'
                })
                response.headers['Content-Type'] = 'application/json; charset=utf-8'
                return response, 400
            
            # Perform OCR
            logger.info(f"Performing OCR with language: {language}")
            ocr_results = perform_ocr(images, language)
            
            # Combine all text
            all_text = ""
            total_lines = 0
            page_details = []
            
            for result in ocr_results:
                page_text = result.get('text', '')
                all_text += page_text + "\n\n"
                total_lines += result.get('line_count', 0)
                
                page_details.append({
                    'page': result['page'],
                    'character_count': len(page_text),
                    'line_count': result.get('line_count', 0),
                    'has_error': 'error' in result
                })
            
            # Calculate metrics
            execution_time = round(time.time() - start_time, 3)
            character_count = len(all_text.strip())
            word_count = len([word for word in all_text.split() if word.strip()])
            
            # Prepare response
            response = {
                'success': True,
                'data': {
                    'extracted_text': all_text.strip(),
                    'language': language,
                    'metrics': {
                        'execution_time_seconds': execution_time,
                        'character_count': character_count,
                        'word_count': word_count,
                        'line_count': total_lines,
                        'page_count': len(images)
                    },
                    'file_info': {
                        'filename': filename,
                        'size_mb': round(os.path.getsize(temp_filepath) / (1024 * 1024), 2)
                    },
                    'page_details': page_details
                },
                'timestamp': datetime.now().isoformat(),
                'processing_info': {
                    'ocr_engine': 'PaddleOCR',
                    'version': '1.0.1'
                }
            }
            
            logger.info(f"OCR completed successfully. Time: {execution_time}s, Characters: {character_count}")
            
            # Create JSON response with explicit content type
            json_response = jsonify(response)
            json_response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return json_response
            
        finally:
            # Clean up temporary file
            try:
                os.remove(temp_filepath)
                logger.info(f"Cleaned up temporary file: {temp_filename}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")
    
    except Exception as e:
        execution_time = round(time.time() - start_time, 3)
        logger.error(f"OCR processing failed: {e}")
        
        error_response = jsonify({
            'success': False,
            'error': 'Processing failed',
            'message': str(e),
            'execution_time_seconds': execution_time,
            'timestamp': datetime.now().isoformat()
        })
        error_response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return error_response, 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    response = jsonify({
        'error': 'File too large',
        'message': 'Maximum file size is 16MB'
    })
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    response = jsonify({
        'error': 'Endpoint not found',
        'message': 'Available endpoints: / (GET), /extract-text (POST)'
    })
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    response = jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    })
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 500

if __name__ == '__main__':
    import os
    # Only print startup messages when not in reloader process
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("🚀 Starting OCR API Service...")
        print("📚 Supported languages: English (en), Vietnamese (vi)")
        print("📄 Supported formats: PDF")
        print("🌐 Access the API at: http://localhost:5000")
        print("📖 API Documentation: http://localhost:5000")
        print("🔧 Test endpoint: POST http://localhost:5000/extract-text")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
