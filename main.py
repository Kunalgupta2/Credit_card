from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import (
    User as SQLAlchemyUser,
    UserDetails,
    UserAddress,
    UserVerification,
    UsercardDetails,
)
from database import SessionLocal
from schemas import (
    UserCreate,
    OtpRequest,
    TokenData,
    UserDetailsCreate,
    UserAddressCreate,
    UserIncome,
    UserDocumentCreate,
    UserCardDetails,
)
from hasing_password import hash_password, verify_password
import uvicorn
from sqlalchemy.orm import Session
import send_mail
import uuid
import os
import requests
import jwt
from jose import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
import os
from aws_tessaract import analyze_id
import logging
from starlette.middleware.cors import CORSMiddleware
from lithic import Lithic

logger = logging.getLogger("/uvicorn.error")
logger.setLevel(logging.DEBUG)


app = FastAPI()
session = {}

Upload_photo_path = "./photos"
Upload_license_path = "./licenses"
os.makedirs(Upload_photo_path, exist_ok=True)
os.makedirs(Upload_license_path, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your client's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except (JWTError, ExpiredSignatureError):
        raise credentials_exception
    user = (
        db.query(SQLAlchemyUser)
        .filter(SQLAlchemyUser.username == token_data.username)
        .first()
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: SQLAlchemyUser = Depends(get_current_user),
):
    print(current_user.__dict__)
    if hasattr(current_user, "disabled") and current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/new_user")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(SQLAlchemyUser).filter(SQLAlchemyUser.email == user.email).first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    existing_username = (
        db.query(SQLAlchemyUser)
        .filter(SQLAlchemyUser.username == user.username)
        .first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="username already taken")

    session_id = str(uuid.uuid4())
    otp = send_mail.send_mail(user.email)
    session[session_id] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.hashed_password),
    }
    return {"session_id": session_id}


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = (
        db.query(SQLAlchemyUser)
        .filter(SQLAlchemyUser.username == form_data.username)
        .first()
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/verify_otp")
def verify_otp(OTP: OtpRequest, db: Session = Depends(get_db)):
    global session
    otp = OTP.otp
    session_id = None
    for key, data in session.items():
        if send_mail.verify_otp(data["email"], otp):
            session_id = key
            break

    if session_id is None:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    new_user = SQLAlchemyUser(
        username=session[session_id]["username"],
        email=session[session_id]["email"],
        hashed_password=session[session_id]["hashed_password"],
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # clean session
    del session[session_id]

    return "User created successfully"


@app.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}&scope=openid%20profile%20email&access_type=offline"
    }


@app.get("/auth/google")
async def auth_google(code: str, db: Session = Depends(get_db)):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch token from Google")

    tokens = response.json()
    access_token = tokens.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_info_response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Failed to fetch user info from Google"
        )

    user_info = user_info_response.json()
    email = user_info["email"]
    name = user_info.get("name", "")

    existing_user = (
        db.query(SQLAlchemyUser).filter(SQLAlchemyUser.email == email).first()
    )
    if existing_user:
        existing_user.last_logged = datetime.utcnow()
        db.commit()
        db.refresh(existing_user)
        return {"message": "Login successful", "user": existing_user.username}

    new_user = SQLAlchemyUser(
        id=str(uuid.uuid4()),
        username=name,
        email=email,
        password=hash_password("default"),
        auth_type="googleAuth",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User registered and login successful",
        "user": new_user.username,
    }


@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        return {"token_payload": payload}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/refresh_token")
def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        new_token = create_access_token(data={"sub": email})

        return {"token": new_token}
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


@app.get("/protected")
def protected_route(current_user: SQLAlchemyUser = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.email}"}


@app.get("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        return {"message": "Logout successful"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/user_details")
def add_user_details(
    user_details: UserDetailsCreate,
    db: Session = Depends(get_db),
    current_user: SQLAlchemyUser = Depends(get_current_active_user),
):

    formated_date = datetime.strptime(user_details.date_of_birth, "%Y-%m-%d").strftime(
        "%d-%m-%Y"
    )
    try:
        user = UserDetails(
            id=current_user.id,
            first_name=user_details.first_name,
            last_name=user_details.last_name,
            phone_number=user_details.phone_number,
            date_of_birth=formated_date,
            gender=user_details.gender,
            annual_income=None,  # Set to None initially
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User details added successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/user_address")
def add_user_address(
    user_address: UserAddressCreate,
    db: Session = Depends(get_db),
    current_user: SQLAlchemyUser = Depends(get_current_active_user),
):
    user = UserAddress(
        id=current_user.id,
        address=user_address.address,
        city=user_address.city,
        state=user_address.state,
        country=user_address.country,
        postal_code=user_address.postal_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User address added successfully"}


@app.post("/user_income")
def add_user_income(
    user_income: UserIncome,
    db: Session = Depends(get_db),
    current_user: SQLAlchemyUser = Depends(get_current_active_user),
):
    try:
        user = db.query(UserDetails).filter(UserDetails.id == current_user.id).first()
        if user is None:
            raise HTTPException(status_code=400, detail="User not found")

        user.annual_income = user_income.Annual_Income
        db.commit()
        db.refresh(user)
        return {
            "message": f"User income added successfully. Annual Income: {user.annual_income}"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user income: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/user_document")
async def add_user_document(
    photo: UploadFile = File(...),
    license: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: SQLAlchemyUser = Depends(get_current_active_user),
):
    try:
        if photo:
            photo_path = os.path.join(Upload_photo_path, photo.filename)
            with open(photo_path, "wb") as f:
                f.write(await photo.read())
        if license:
            license_path = os.path.join(Upload_license_path, license.filename)
            with open(license_path, "wb") as f:
                f.write(await license.read())

        user = UserVerification(
            id=current_user.id, photo=photo_path, license=license_path
        )
        result = kyc_verification(license_path, db, current_user.id)
        if not result.get("dob_match") and not result.get("name_match"):
            if photo_path is not None:
                os.remove(photo_path)
            if license_path is not None:
                os.remove(license_path)
            return {
                "message": "Failed to upload document",
                "verification_summary": result.get("verification_summary"),
            }
        else:
            db.add(user)
            db.commit()
            db.refresh(user)
            return {
                "message": "User document added successfully",
                "verification_summary": result.get("verification_summary"),
            }
    except Exception as e:
        logger.error(f"Error in add_user_document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def kyc_verification(license_path, db: Session = Depends(get_db), id: str = ""):
    try:
        data = analyze_id(
            license_path,
            os.getenv("AWS_ACCESS_KEY_ID"),
            os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        print(data)
        extracted_dob_str = data.get("DATE_OF_BIRTH")
        if not extracted_dob_str:
            logger.error("Date of birth not found in ID")
            return {
                "dob_match": False,
                "verification_summary": "Date of birth not found in document",
            }

        try:
            extracted_dob = datetime.strptime(extracted_dob_str, "%d-%m-%Y").date()
        except ValueError:
            logger.error("Invalid date of birth format")
            return {
                "dob_match": False,
                "verification_summary": "Invalid date of birth format in document",
            }

        # Fetch the user details from the database
        user = db.query(UserDetails).filter(UserDetails.id == id).first()
        if not user:
            logger.error("User not found")
            return {"dob_match": False, "verification_summary": "User not found"}

        # Validate the user's full name from the document
        document_full_name = f"{data.get('FIRST_NAME')} {data.get('LAST_NAME')}"
        database_full_name = user.first_name + " " + user.last_name
        name_match = document_full_name == database_full_name
        print(name_match)

        # Validate the date of birth
        dob_match = (
            extracted_dob == datetime.strptime(user.date_of_birth, "%d-%m-%Y").date()
        )
        print(dob_match)

        # Ensure the user is at least 18 years old
        current_date = datetime.now().date()
        age = (current_date - extracted_dob).days // 365
        if age < 18:
            logger.error("User must be at least 18 years old")
            return {
                "dob_match": False,
                "verification_summary": "User must be at least 18 years old",
            }

        # Validate the expiry date of the document
        expiry_date_str = data.get("EXPIRATION_DATE")
        if not expiry_date_str:
            logger.error("Expiry date not found in ID")
            return {
                "dob_match": dob_match,
                "name_match": name_match,
                "verification_summary": "Expiry date not found",
            }

        try:
            expiry_date = datetime.strptime(expiry_date_str, "%d-%m-%Y").date()
        except ValueError:
            logger.error("Invalid expiry date format")
            return {
                "dob_match": dob_match,
                "name_match": name_match,
                "verification_summary": "Invalid expiry date format",
            }

        if expiry_date <= datetime.strptime("01-05-2013", "%d-%m-%Y").date():
            logger.error("Document has expired")
            return {
                "dob_match": dob_match,
                "name_match": name_match,
                "verification_summary": "Document has expired",
            }

        # Return all verification details
        return {
            "name_match": name_match,
            "dob_match": dob_match,
            "database_name": database_full_name,
            "document_name": document_full_name,
            "database_dob": str(user.date_of_birth),
            "document_dob": extracted_dob_str,
            "verification_summary": "KYC verification completed successfully",
        }

    except Exception as e:
        logger.error(f"Error performing KYC verification: {e}")
        return {
            "dob_match": False,
            "verification_summary": f"Error performing KYC verification: {e}",
        }


client = Lithic(
    api_key=os.getenv("LITHIC_API_KEY"),
    environment="sandbox",
)
card_program_token = "00000000-0000-0000-1000-000000000000"


@app.post("/user_creditcard")
def add_user_creditcard(
    current_user: SQLAlchemyUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    existing_card = (
        db.query(UsercardDetails).filter(UsercardDetails.id == current_user.id).first()
    )
    if existing_card:
        raise HTTPException(status_code=400, detail="Card already exists")

    else:

        user = db.query(UserDetails).filter(UserDetails.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User card details not found")
        user_address = (
            db.query(UserAddress).filter(UserAddress.id == current_user.id).first()
        )

        user_email = (
            db.query(SQLAlchemyUser)
            .filter(SQLAlchemyUser.id == current_user.id)
            .first()
        )

        shipping_address = {
            "address1": user_address.address,
            "address2": "",
            "city": user_address.city,
            "state": user_address.state,
            "postal_code": user_address.postal_code,
            "email": user_email.email,
            "country": user_address.country,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        current_date = datetime.now().strftime("%Y-%m-%d")
        exp_month = current_date[5:7]
        exp_year = str(int(current_date[0:4]) + 6)
        shipping_method = "STANDARD"
        memo = user.first_name + " " + user.last_name
        spend_limit = int(user.annual_income) % 10
        spend_limit_duration = "MONTHLY"

        try:
            card = client.cards.create(
                shipping_address=shipping_address,
                type="VIRTUAL",
                card_program_token=card_program_token,
                exp_month=exp_month,
                exp_year=exp_year,
                memo=memo,
                shipping_method=shipping_method,
                spend_limit=spend_limit,
                spend_limit_duration=spend_limit_duration,
                state="OPEN",
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        logger.info(f"Card created successfully: {card.account_token}")

        card_details = UsercardDetails(
            id=current_user.id,
            account_id=card.account_token,  # Added missing comma here
            created_at=card.created,
            expiry_date=f"{card.exp_month}/{card.exp_year}",
            spending_limit=card.spend_limit,
            cvv=card.cvv,
            card_holder_name=card.memo,
            date_issued=card.created,
            card_number=card.pan,
        )
        db.add(card_details)
        db.commit()
        db.refresh(card_details)
        return {"message": "Card details added successfully"}


@app.get("/check_user_state")
def check_user_statess(
    db: Session = Depends(get_db),
    current_user: SQLAlchemyUser = Depends(get_current_active_user),
):
    user = db.query(UserDetails).filter(UserDetails.id == current_user.id).first()
    user_address = (
        db.query(UserAddress).filter(UserAddress.id == current_user.id).first()
    )
    user_documents = (
        db.query(UserVerification)
        .filter(UserVerification.id == current_user.id)
        .first()
    )
    if not user:
        return "user"
    elif not user_address:
        return "address"
    elif user.annual_income is None:
        return "income"
    elif not user_documents:
        return "documents"
    else:
        return "dashboard"


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
