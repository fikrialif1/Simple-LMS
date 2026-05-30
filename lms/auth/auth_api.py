from ninja import Router
from ninja.errors import HttpError
from .schemas import (
    RegisterSchema,
    UpdateProfileSchema,
    LoginSchema,
    RefreshSchema
)
from ..models import User
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken, TokenError

router = Router(tags=["Authentication"])

jwt_auth = JWTAuth()


# REGISTER
@router.post("/register")
def register(request, data: RegisterSchema):

    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username sudah digunakan")

    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email sudah digunakan")

    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role
    )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }


# LOGIN
@router.post("/login")
def login(request, data: LoginSchema):

    user = authenticate(
        username=data.username,
        password=data.password
    )

    if not user:
        raise HttpError(
            401,
            "Username atau password salah"
        )

    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


# REFRESH TOKEN
@router.post("/refresh")
def refresh_token(request, data: RefreshSchema):

    try:
        token = RefreshToken(data.refresh)

        return {
            "access": str(token.access_token)
        }

    except TokenError:
        raise HttpError(
            401,
            "Refresh token tidak valid"
        )


# GET PROFILE
@router.get("/me", auth=jwt_auth)
def me(request):

    return {
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "role": request.user.role
    }


# UPDATE PROFILE
@router.put("/me", auth=jwt_auth)
def update_me(request, data: UpdateProfileSchema):

    user = request.user

    if data.username:
        user.username = data.username

    if data.email:
        user.email = data.email

    user.save()

    return {
        "message": "Profile berhasil diperbarui"
    }