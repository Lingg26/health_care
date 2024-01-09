import os

PROJECT_NAME: str = 'Health Care'
APP_ENV: str = os.getenv('APP_ENV', 'local')
# 60 minutes * 24 hours * 7 days = 10800 minutes of 7 days
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES') or 60)
REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES') or 10080)
API_V1_STR: str = '/api/v1'
SECRET_KEY: str = os.getenv(
    'APP_SECRET_KEY', 'cf1e7b0c69aa03f359d121104b73a924bd2a6d8839daf8e5f057735dfdf1155e'
)
APP_ROOT_PATH = os.getenv('APP_ROOT_PATH')
DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_URL = DATABASE_URL.replace('?reconnect=true', '')
if 'charset=utf8mb4' not in DATABASE_URL:
    DATABASE_URL += '?charset=utf8mb4'
CORS_ALLOWED_ORIGINS = [i.strip() for i in os.getenv('CORS_ALLOWED_ORIGINS', '*').split(',')]
MASTER_KEY = os.getenv('MASTER_KEY', '@#s58sEv2FA')

GOOGLE_IOS_APP_CLIENT_ID = os.getenv("GOOGLE_IOS_APP_CLIENT_ID")
GOOGLE_ANDROID_APP_CLIENT_ID = os.getenv("GOOGLE_ANDROID_APP_CLIENT_ID")

# Validate file
ALLOWED_IMAGE_EXTENSIONS = (
    os.getenv('ALLOWED_IMAGE_EXTENSIONS', 'jpeg,png,gif,jpg').replace(' ', '').split(',')
)  # Default = jpeg,png,gif
ALLOWED_IMAGE_SIZE = int(os.getenv('ALLOWED_IMAGE_SIZE', 20971520))  # Default = 200MB

MASTER_KEY = os.getenv('MASTER_KEY', '@#s58sEv2FA')
DISTANCE_SEARCH = os.getenv('DISTANCE_SEARCH', '100m')


MAIL_USERNAME = os.getenv('EMAIL_HOST_USER', "bjmcontran@gmail.com")
MAIL_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'gzfmttvuyooxvklp')
MAIL_PORT = os.getenv('EMAIL_PORT', 587)
MAIL_SERVER = os.getenv('EMAIL_HOST', 'smtp.gmail.com')

PASSWORD_DEFAULT = "Admin1234@"
#VNPAY
VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE', 'EZ843100')
VNPAY_RETURN_URL = 'https://localhost03012024.com/payment_return'
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
VNPAY_HASH_SECRET_KEY = 'RRLGQGNPNVBHDDBNGJOOWILTVOZHAYXQ'


