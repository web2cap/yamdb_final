import pytest
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()


class Test00UserRegistration:
    url_signup = '/api/v1/auth/signup/'
    url_token = '/api/v1/auth/token/'
    url_admin_create_user = '/api/v1/users/'

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_signup(self, client):
        request_type = 'POST'
        response = client.post(self.url_signup)

        assert response.status_code != 404, (
            f'Page `{self.url_signup}` not found, check address in *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Check that when {request_type} request `{self.url_signup}` without parameters'
            f'user is not created and status is returned {code}'
        )
        response_json = response.json()
        empty_fields = ['email', 'username']
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Check that when {request_type} request `{self.url_signup}` without parameters'
                f'in the response there is a message about which fields are filled in incorrectly'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_invalid_data_signup(self, client):
        invalid_email = 'invalid_email'
        invalid_username = 'invalid_username@yamdb.fake'

        invalid_data = {
            'email': invalid_email,
            'username': invalid_username
        }
        request_type = 'POST'
        response = client.post(self.url_signup, data=invalid_data)

        assert response.status_code != 404, (
            f'Page `{self.url_signup}` not found, check address in *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Check that when {request_type} request `{self.url_signup}` with invalid data '
            f'user is not created and status is returned {code}'
        )

        response_json = response.json()
        invalid_fields = ['email']
        for field in invalid_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Check that when {request_type} request `{self.url_signup}` with invalid parameters, '
                f'in the response there is a message about which fields are filled in incorrectly'
            )

        valid_email = 'validemail@yamdb.fake'
        invalid_data = {
            'email': valid_email,
        }
        response = client.post(self.url_signup, data=invalid_data)
        assert response.status_code == code, (
            f'Check that with {request_type} the request is `{self.url_signup}` without username '
            f'cannot create user and return status {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_valid_data_user_signup(self, client):

        valid_email = 'valid@yamdb.fake'
        valid_username = 'valid_username'
        outbox_before_count = len(mail.outbox)

        valid_data = {
            'email': valid_email,
            'username': valid_username
        }
        request_type = 'POST'
        response = client.post(self.url_signup, data=valid_data)
        outbox_after = mail.outbox  # email outbox after user create

        assert response.status_code != 404, (
            f'Page `{self.url_signup}` not found, check this address in *urls.py*'
        )

        code = 200
        assert response.status_code == code, (
            f'Check that when {request_type} request `{self.url_signup}` with valid data'
            f'user is created and status is returned {code}'
        )
        assert response.json() == valid_data, (
            f'Check that when {request_type} request `{self.url_signup}` with valid data'
            f'user is created and status is returned {code}'
        )

        new_user = User.objects.filter(email=valid_email)
        assert new_user.exists(), (
            f'Check that when {request_type} request `{self.url_signup}` with valid data'
            f'user is created and status is returned {code}'
        )

        # Test confirmation code
        assert len(outbox_after) == outbox_before_count + 1, (
            f'Check that when {request_type} request `{self.url_signup}` with valid data, '
            f'The user receives an email with a verification code.'
        )
        assert valid_email in outbox_after[0].to, (
            f'Check that when {request_type} request `{self.url_signup}` with valid data, '
            f'the user receives an email with a confirmation code to the email address he provided during registration'
        )

        new_user.delete()

    @pytest.mark.django_db(transaction=True)
    def test_00_valid_data_admin_create_user(self, admin_client):

        valid_email = 'valid@yamdb.fake'
        valid_username = 'valid_username'
        outbox_before_count = len(mail.outbox)

        valid_data = {
            'email': valid_email,
            'username': valid_username
        }
        request_type = 'POST'
        response = admin_client.post(self.url_admin_create_user, data=valid_data)
        outbox_after = mail.outbox

        assert response.status_code != 404, (
            f'Page `{self.url_admin_create_user}` not found, check this address in *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Check that when {request_type} request `{self.url_admin_create_user}` with valid data '
            f'as administrator, user is created and status is returned {code}'
        )
        response_json = response.json()
        for field in valid_data:
            assert field in response_json and valid_data.get(field) == response_json.get(field), (
                f'Check that when {request_type} request `{self.url_admin_create_user}` with valid data '
                f'on behalf of the administrator, the response is the created user object in the form of a dictionary'
            )

        new_user = User.objects.filter(email=valid_email)
        assert new_user.exists(), (
            f'Check that when {request_type} request `{self.url_admin_create_user}` with valid data '
            f'as administrator, in the database user is created and status is returned {code}'
        )

        # Test confirmation code not sent to user after admin registers him
        assert len(outbox_after) == outbox_before_count, (
            f'Check that when {request_type} request `{self.url_admin_create_user}` with valid data '
            f'on behalf of the administrator, the user does NOT receive an email with a confirmation code'
        )

        new_user.delete()

    @pytest.mark.django_db(transaction=True)
    def test_00_obtain_jwt_token_invalid_data(self, client):

        request_type = 'POST'
        response = client.post(self.url_token)
        assert response.status_code != 404, (
            f'Page `{self.url_token}` not found, check this address in *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Check that when POST requesting `{self.url_token}` without parameters,'
            f'return status {code}'
        )

        invalid_data = {
            'confirmation_code': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        assert response.status_code == code, (
            f'Check that when you POST request `{self.url_token}` without username,'
            f'return status {code}'
        )

        invalid_data = {
            'username': 'unexisting_user',
            'confirmation_code': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        code = 404
        assert response.status_code == code, (
            f'Check that when POSTing a `{self.url_token}` request with a non-existent username,'
            f'return status {code}'
        )

        valid_email = 'valid@yamdb.fake'
        valid_username = 'valid_username'

        valid_data = {
            'email': valid_email,
            'username': valid_username
        }
        response = client.post(self.url_signup, data=valid_data)
        code = 200
        assert response.status_code == code, (
            f'Check that when {request_type} request `{self.url_signup}` with valid data'
            f'user is created and status is returned {code}'
        )

        invalid_data = {
            'username': valid_username,
            'confirmation_code': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        code = 400
        assert response.status_code == code, (
            f'Check that when POSTing `{self.url_token}` with a valid username,'
            f'but invalid confirmation_code, return status {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_registration_me_username_restricted(self, client):
        valid_email = 'valid@yamdb.fake'
        invalid_username = 'me'
        request_type = 'POST'

        valid_data = {
            'email': valid_email,
            'username': invalid_username
        }
        response = client.post(self.url_signup, data=valid_data)
        code = 400
        assert response.status_code == code, (
            f'Check that on {request_type} the request is `{self.url_signup}` '
            f'cannot create user with username = "me" and return status {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_registration_same_email_restricted(self, client):
        valid_email_1 = 'test_duplicate_1@yamdb.fake'
        valid_email_2 = 'test_duplicate_2@yamdb.fake'
        valid_username_1 = 'valid_username_1'
        valid_username_2 = 'valid_username_2'
        request_type = 'POST'

        valid_data = {
            'email': valid_email_1,
            'username': valid_username_1
        }
        response = client.post(self.url_signup, data=valid_data)
        code = 200
        assert response.status_code == code, (
            f'Check that on {request_type} the request is `{self.url_signup}` '
            f'you can create a user with valid data and return status {code}'
        )

        duplicate_email_data = {
            'email': valid_email_1,
            'username': valid_username_2
        }
        response = client.post(self.url_signup, data=duplicate_email_data)
        code = 400
        assert response.status_code == code, (
            f'Check that on {request_type} the request is `{self.url_signup}` cannot be created '
            f'user whose email is already registered and return status {code}'
        )
        duplicate_username_data = {
            'email': valid_email_2,
            'username': valid_username_1
        }
        response = client.post(self.url_signup, data=duplicate_username_data)
        assert response.status_code == code, (
            f'Check that on {request_type} the request is `{self.url_signup}` cannot be created '
            f'user whose username is already registered and return status {code}'
        )
