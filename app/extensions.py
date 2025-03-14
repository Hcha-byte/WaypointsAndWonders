# app/extensions.py
from flask_mail import Mail

import cloudinary
import cloudinary.uploader

mail = Mail()


cloudinary.config(
    cloud_name="dao2ekwrd",
    api_key="959777166196123",
    api_secret="CUooeSeQeIL5yFh7wyXlpJ20aJY"
)