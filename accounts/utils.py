from django.core.mail import send_mail
from django.conf import settings


#sent the otp to the email of user
def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    print(otp,email)
    send_mail(subject, message, from_email, recipient_list)