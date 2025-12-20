from core.models import User


def create_user(*, name: str, email: str | None = None, password: str | None = None) -> User:
    return User.objects.create_user(
        name=name,
        email=email,
        password=password,
    )
