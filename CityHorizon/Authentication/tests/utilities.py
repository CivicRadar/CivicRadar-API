from Authentication.models import User


def create_user(Email, Password, FullName, Type, **extra_args):
    user = User(FullName=FullName, Email=Email, Type=Type, **extra_args)
    user.set_password(Password)
    user.save()
    return user
