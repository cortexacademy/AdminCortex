import os
from datetime import datetime

def custom_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    original_filename = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    new_filename = f'{timestamp}_{original_filename}.{ext}'
    return os.path.join('images/', new_filename)
