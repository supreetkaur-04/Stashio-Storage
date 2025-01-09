# storage/utils.py

from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']

def validate_file(file):
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError("File size exceeds the 10MB limit.")
    if file.name.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
        raise ValidationError("Invalid file type.")
