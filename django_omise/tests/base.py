from django.contrib.auth import get_user_model

from django.test import Client, TestCase

User = get_user_model()


class ClientAndUserBaseTestCase(TestCase):
    """Base TestCase with utilites to create user and login client."""

    def setUp(self):
        """Class setup."""
        self.client = Client()
        self.index_url = "/"
        self.login()

    def create_user(self):
        """Create user and returns username, password tuple."""
        username, password = "admin", "test"
        user = User.objects.get_or_create(
            username=username,
            email="admin@test.com",
            is_superuser=True,
            is_staff=True,
        )[0]
        user.set_password(password)
        user.save()
        self.user = user
        return (username, password)

    def login(self):
        """Log in client session."""
        username, password = self.create_user()
        self.client.login(username=username, password=password)
