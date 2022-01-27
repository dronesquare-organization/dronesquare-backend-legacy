from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def create_user(
        self, email, name, phoneNumber, organization, password, **extra_fields
    ):
        """
        Create and save a User with the given email and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phoneNumber=phoneNumber,
            organization=organization,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(
        self, email, name, phoneNumber, organization, password, **extra_fields
    ):
        """
        Create and save a SuperUser with the given email and password.
        """
        self.model(
            email=self.normalize_email(email),
            name=name,
            phoneNumber=phoneNumber,
            organization=organization,
            **extra_fields
        )
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email, name, phoneNumber, organization, password, **extra_fields
        )
