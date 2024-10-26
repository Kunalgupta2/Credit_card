import os
import yagmail
import random
from dotenv import load_dotenv


cache = {}

mail = yagmail.SMTP(os.getenv("email"), os.getenv("password"))


def send_mail(to_mail):
    otp = random.randint(100000, 999999)
    mail.send(to=to_mail, subject="Your login OTP ", contents=f"your otp is {otp}")
    cache[to_mail] = str(otp)
    print(cache)
    return f"OTP sent to {to_mail}"


def verify_otp(to_mail, otp):
    if cache.get(to_mail) == (otp):
        del cache[to_mail]
        print(cache)
        return True

    else:
        return False
