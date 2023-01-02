import pytest
from django.contrib.auth import get_user_model

from .common import auth_client, create_users_api


class Test01UserAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_users_not_authenticated(self, client):
        response = client.get('/api/v1/users/')

        assert response.status_code != 404, (
            'Page `/api/v1/users/` not found, check this address in *urls.py*'
        )

        assert response.status_code == 401, (
            'Check that a GET request to `/api/v1/users/` without an authorization token returns status 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_users_username_not_authenticated(self, client, admin):
        response = client.get(f'/api/v1/users/{admin.username}/')

        assert response.status_code != 404, (
            'Page `/api/v1/users/{username}/` not found, check this address in *urls.py*'
        )

        assert response.status_code == 401, (
            'Check that a GET request to `/api/v1/users/{username}/` without an authorization token returns status 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_users_me_not_authenticated(self, client):
        response = client.get('/api/v1/users/me/')

        assert response.status_code != 404, (
            'Page `/api/v1/users/me/` not found, check this address in *urls.py*'
        )

        assert response.status_code == 401, (
            'Check that a GET request to `/api/v1/users/me/` without an authorization token returns status 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_users_get_admin(self, admin_client, admin):
        response = admin_client.get('/api/v1/users/')
        assert response.status_code != 404, (
            'Page `/api/v1/users/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/users/` with an authorization token returns status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'Not found parameter: `count`'
        )
        assert 'next' in data, (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'Not found parameter: `next`'
        )
        assert 'previous' in data, (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'Not found parameter: `previous`'
        )
        assert 'results' in data, (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'Not found parameter: `results`'
        )
        assert data['count'] == 1, (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'The value of the `count` parameter is not correct'
        )
        assert type(data['results']) == list, (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'The type of the `results` parameter must be a list'
        )
        assert (
            len(data['results']) == 1
            and data['results'][0].get('username') == admin.username
            and data['results'][0].get('email') == admin.email
        ), (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'The value of the `results` parameter is not correct'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_02_users_get_search(self, admin_client, admin):
        url = '/api/v1/users/'
        search_url = f'{url}?search={admin.username}'
        response = admin_client.get(search_url)
        assert response.status_code != 404, (
            'Page `/api/v1/users/?search={username}` not found, check this address in *urls.py*'
        )
        reponse_json = response.json()
        assert 'results' in reponse_json and isinstance(reponse_json.get('results'), list), (
            'Check that on GET request `/api/v1/users/?search={username}` '
            'the results are returned under the `results` key and as a list.'
        )
        users_count = get_user_model().objects.filter(username=admin.username).count()
        assert len(reponse_json['results']) == users_count, (
            'Check that on GET request `/api/v1/users/?search={username}` '
            'only the user with the username specified in the search is returned'
        )
        admin_as_dict = {
            'username': admin.username,
            'email': admin.email,
            'role': admin.role,
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'bio': admin.bio
        }
        assert reponse_json['results'] == [admin_as_dict], (
            'Check that on GET request `/api/v1/users/?search={username}` '
            'the searched user is returned with all required fields, including `bio` and `role`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_01_users_get_admin_only(self, user_client):
        url = '/api/v1/users/'
        response = user_client.get(url)
        assert response.status_code != 404, (
            f'Page `{url}` not found, check this address in *urls.py*'
        )
        status = 403
        assert response.status_code == status, (
            f'Check that a non-admin GET request for `{url}` returns {status}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_01_users_post_admin(self, admin_client, admin):
        empty_data = {}
        response = admin_client.post('/api/v1/users/', data=empty_data)
        assert response.status_code == 400, (
            'Check that POSTing `/api/v1/users/` with empty data returns 400'
        )
        no_email_data = {
            'username': 'TestUser_noemail',
            'role': 'user'
        }
        response = admin_client.post('/api/v1/users/', data=no_email_data)
        assert response.status_code == 400, (
            'Check that when you POST request to `/api/v1/users/` without email, it returns status 400'
        )
        valid_email = 'valid_email@yamdb.fake'
        no_username_data = {
            'email': valid_email,
            'role': 'user'
        }
        response = admin_client.post('/api/v1/users/', data=no_username_data)
        assert response.status_code == 400, (
            'Check that POST request to `/api/v1/users/` without username returns status 400'
        )
        duplicate_email = {
            'username': 'TestUser_duplicate',
            'role': 'user',
            'email': admin.email
        }
        response = admin_client.post('/api/v1/users/', data=duplicate_email)
        assert response.status_code == 400, (
            'Check that when you POST a request to `/api/v1/users/` with a pre-existing email, it returns status 400. '
            '`Email` must be unique for each user'
        )
        duplicate_username = {
            'username': admin.username,
            'role': 'user',
            'email': valid_email
        }
        response = admin_client.post('/api/v1/users/', data=duplicate_username)
        assert response.status_code == 400, (
            'Check that when you POST a request to `/api/v1/users/` with a pre-existing email, it returns status 400. '
            '`Email` must be unique for each user'
        )
        data = {
            'username': admin.username,
            'role': 'user',
            'email': 'testuser@yamdb.fake'
        }
        response = admin_client.post('/api/v1/users/', data=data)
        assert response.status_code == 400, (
            'Check that when POSTing `/api/v1/users/` with invalid data returns status 400.'
            '`Username` must be unique for each user'
        )
        valid_data = {
            'username': 'TestUser_2',
            'role': 'user',
            'email': 'testuser2@yamdb.fake'
        }
        response = admin_client.post('/api/v1/users/', data=valid_data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/users/` with valid data returns 201.'
        )
        valid_data = {
            'username': 'TestUser_3',
            'email': 'testuser3@yamdb.fake'
        }
        response = admin_client.post('/api/v1/users/', data=valid_data)
        assert response.status_code == 201, (
            'Check that when POSTing `/api/v1/users/`, when creating a user without specifying a role, '
            'by default, the user role is given and status 201 is returned.'
        )
        assert response.json().get('role') == 'user', (
            'Check that when POSTing `/api/v1/users/`, when creating a user without specifying a role, '
            'by default, the user role is given and status 201 is returned.'
        )
        data = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'username': 'test_username',
            'bio': 'test bio',
            'role': 'moderator',
            'email': 'testmoder2@yamdb.fake'
        }
        response = admin_client.post('/api/v1/users/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/users/` with correct data returns 201.'
        )
        response_data = response.json()
        assert response_data.get('first_name') == data['first_name'], (
            'Check that POSTing `/api/v1/users/` with correct data returns `first_name`.'
        )
        assert response_data.get('last_name') == data['last_name'], (
            'Check that POSTing `/api/v1/users/` with correct data returns `last_name`.'
        )
        assert response_data.get('username') == data['username'], (
            'Check that POSTing `/api/v1/users/` with correct data returns `username`.'
        )
        assert response_data.get('bio') == data['bio'], (
            'Check that POSTing `/api/v1/users/` with correct data returns `bio`.'
        )
        assert response_data.get('role') == data['role'], (
            'Check that POSTing `/api/v1/users/` with correct data returns `role`.'
        )
        assert response_data.get('email') == data['email'], (
            'Check that POSTing `/api/v1/users/` with correct data returns `email`.'
        )
        User = get_user_model()
        users = User.objects.all()
        assert get_user_model().objects.count() == users.count(), (
            'Check that when you POST to `/api/v1/users/` you are creating users.'
        )
        response = admin_client.get('/api/v1/users/')
        data = response.json()
        assert len(data['results']) == users.count(), (
            'Check that when you make a GET request to `/api/v1/users/` you return data with pagination. '
            'The value of the `results` parameter is not correct'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_02_users_post_user_superuser(self, user_superuser_client):
        users = get_user_model().objects.all()
        users_before = users.count()
        valid_data = {
            'username': 'TestUser_3',
            'role': 'user',
            'email': 'testuser3@yamdb.fake'
        }
        response = user_superuser_client.post('/api/v1/users/', data=valid_data)
        assert response.status_code == 201, (
            'Check that when POSTing `/api/v1/users/` from superuser , '
            'with correct data, return status 201.'
        )
        users_after = users.count()
        assert users_after == users_before + 1, (
            'Check that when POSTing `/api/v1/users/` from superuser , '
            'with the correct data, a user is created.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_users_username_get_admin(self, admin_client, admin):
        user, moderator = create_users_api(admin_client)
        response = admin_client.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code != 404, (
            'Page `/api/v1/users/{username}/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/users/{username}/` with an admin token returns status 200'
        )
        response_data = response.json()
        assert response_data.get('username') == admin.username, (
            'Check that when GET requesting `/api/v1/users/{username}/` you return `username`.'
        )
        assert response_data.get('email') == admin.email, (
            'Check that when GET requesting `/api/v1/users/{username}/` you return `email`.'
        )

        response = admin_client.get(f'/api/v1/users/{moderator.username}/')
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/users/{username}/` with an authorization token returns status 200'
        )
        response_data = response.json()
        assert response_data.get('username') == moderator.username, (
            'Check that when GET requesting `/api/v1/users/{username}/` you return `username`.'
        )
        assert response_data.get('email') == moderator.email, (
            'Check that when GET requesting `/api/v1/users/{username}/` you return `email`.'
        )
        assert response_data.get('first_name') == moderator.first_name, (
            'Check that when GET requesting `/api/v1/users/` you return `first_name`.'
        )
        assert response_data.get('last_name') == moderator.last_name, (
            'Check that when GET requesting `/api/v1/users/` you return `last_name`.'
        )
        assert response_data.get('bio') == moderator.bio, (
            'Check that when GET requesting `/api/v1/users/` you return `bio`.'
        )
        assert response_data.get('role') == moderator.role, (
            'Check that when GET requesting `/api/v1/users/` you return `role`.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_users_username_get_not_admin(self, moderator_client, admin):
        response = moderator_client.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code != 404, (
            'Page `/api/v1/users/{username}/` not found, check this address in *urls.py*'
        )
        code = 403
        assert response.status_code == code, (
            'Check that on GET request `/api/v1/users/{username}/`'
            f'with admin token return status {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_01_users_username_patch_admin(self, admin_client, admin):
        user, moderator = create_users_api(admin_client)
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = admin_client.patch(f'/api/v1/users/{admin.username}/', data=data)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/users/{username}/` '
            'with authorization token returns status 200'
        )
        test_admin = get_user_model().objects.get(username=admin.username)
        assert test_admin.first_name == data['first_name'], (
            'Check that on PATCH request `/api/v1/users/{username}/`change the data.'
        )
        assert test_admin.last_name == data['last_name'], (
            'Check that on PATCH request `/api/v1/users/{username}/`change the data.'
        )
        response = admin_client.patch(f'/api/v1/users/{user.username}/', data={'role': 'admin'})
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/users/{username}/` '
            'from a user with the admin role, you can change the user role'
        )
        response = admin_client.patch(f'/api/v1/users/{user.username}/', data={'role': 'owner'})
        assert response.status_code == 400, (
            'Check that on PATCH request `/api/v1/users/{username}/` '
            'from a user with the admin role, you cannot assign arbitrary user roles'
            'and returns status 400'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_02_users_username_patch_moderator(self, moderator_client, user):
        data = {
            'first_name': 'New USer Firstname',
            'last_name': 'New USer Lastname',
            'bio': 'new user bio'
        }
        response = moderator_client.patch(f'/api/v1/users/{user.username}/', data=data)
        assert response.status_code == 403, (
            'Check that on PATCH request `/api/v1/users/{username}/` '
            'a user with the moderator role cannot change the data of other users'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_03_users_username_patch_user(self, user_client, user):
        data = {
            'first_name': 'New USer Firstname',
            'last_name': 'New USer Lastname',
            'bio': 'new user bio'
        }
        response = user_client.patch(f'/api/v1/users/{user.username}/', data=data)
        assert response.status_code == 403, (
            'Check that on PATCH request `/api/v1/users/{username}/` '
            'a user with the user role cannot change the data of other users'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_05_users_username_put_user_restricted(self, user_client, user):
        data = {
            'first_name': 'New USer Firstname',
            'last_name': 'New USer Lastname',
            'bio': 'new user bio'
        }
        response = user_client.put(f'/api/v1/users/{user.username}/', data=data)
        code = 403
        assert response.status_code == code, (
            'Check that PUT request to `/api/v1/users/{username}/`'
            f'not available and the status is returned {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_01_users_username_delete_admin(self, admin_client):
        user, moderator = create_users_api(admin_client)
        response = admin_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 204, (
            'Check that DELETE request `/api/v1/users/{username}/` returns status 204'
        )
        assert get_user_model().objects.count() == 2, (
            'Check that when you DELETE request `/api/v1/users/{username}/` you delete the user'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_02_users_username_delete_moderator(self, moderator_client, user):
        users_before = get_user_model().objects.count()
        response = moderator_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 403, (
            'Check that on DELETE request `/api/v1/users/{username}/` '
            'not from admin, return status 403'
        )
        assert get_user_model().objects.count() == users_before, (
            'Check that on DELETE request `/api/v1/users/{username}/` '
            'not from the admin, do not delete the user'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_03_users_username_delete_user(self, user_client, user):
        users_before = get_user_model().objects.count()
        response = user_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 403, (
            'Check that on DELETE request `/api/v1/users/{username}/`  '
            'not from admin, return status 403'
        )
        assert get_user_model().objects.count() == users_before, (
            'Check that on DELETE request `/api/v1/users/{username}/`  '
            'not from the admin, do not delete the user'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_04_users_username_delete_superuser(self, user_superuser_client, user):
        users_before = get_user_model().objects.count()
        response = user_superuser_client.delete(f'/api/v1/users/{user.username}/')
        code = 204
        assert response.status_code == code, (
            'Check that on DELETE request `/api/v1/users/{username}/`  '
            f'from superuser, return status {code}'
        )
        assert get_user_model().objects.count() == users_before - 1, (
            'Check that on DELETE request `/api/v1/users/{username}/`  '
            'from superuser, the user is removed.'
        )

    def check_permissions(self, user, user_name, admin):
        client_user = auth_client(user)
        response = client_user.get('/api/v1/users/')
        assert response.status_code == 403, (
            f'Check that on GET request `/api/v1/users/` '
            f'with auth token {user_name} return status 403'
        )
        data = {
            'username': 'TestUser9876',
            'role': 'user',
            'email': 'testuser9876@yamdb.fake'
        }
        response = client_user.post('/api/v1/users/', data=data)
        assert response.status_code == 403, (
            f'Check that when you POST a request to `/api/v1/users/`'
            f'with auth token {user_name} return status 403'
        )

        response = client_user.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 403, (
            f'Check that on GET request `/api/v1/users/{{username}}/` '
            f'with auth token {user_name} return status 403'
        )
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = client_user.patch(f'/api/v1/users/{admin.username}/', data=data)
        assert response.status_code == 403, (
            f'Check that on PATCH request `/api/v1/users/{{username}}/` '
            f'with auth token {user_name} return status 403'
        )
        response = client_user.delete(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 403, (
            f'Check that on DELETE request `/api/v1/users/{{username}}/` '
            f'with auth token {user_name} return status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_users_check_permissions(self, admin_client, admin):
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'regular user', admin)
        self.check_permissions(moderator, 'moderator', admin)

    @pytest.mark.django_db(transaction=True)
    def test_10_users_me_get_admin(self, admin_client, admin):
        user, moderator = create_users_api(admin_client)
        response = admin_client.get('/api/v1/users/me/')
        assert response.status_code == 200, (
            'Check that GET request to `/api/v1/users/me/` from admin returns status 200'
        )
        response_data = response.json()
        assert response_data.get('username') == admin.username, (
            'Check that a GET request to `/api/v1/users/me/` returns user data'
        )
        client_user = auth_client(moderator)
        response = client_user.get('/api/v1/users/me/')
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/users/me/` with authorization token returns status 200'
        )
        response_data = response.json()
        assert response_data.get('username') == moderator.username, (
            'Check that a GET request to `/api/v1/users/me/` returns user data'
        )
        assert response_data.get('role') == 'moderator', (
            'Check that a GET request to `/api/v1/users/me/` returns user data'
        )
        assert response_data.get('email') == moderator.email, (
            'Check that a GET request to `/api/v1/users/me/` returns user data'
        )
        assert response_data.get('bio') == moderator.bio, (
            'Check that a GET request to `/api/v1/users/me/` returns user data'
        )
        response = client_user.delete('/api/v1/users/me/')
        assert response.status_code == 405, (
            'Check that DELETE request to `/api/v1/users/me/` returns status 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_01_users_me_patch_admin(self, admin_client):
        user, moderator = create_users_api(admin_client)
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = admin_client.patch('/api/v1/users/me/', data=data)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/users/me/` with authorization token returns status 200'
        )
        response_data = response.json()
        assert response_data.get('bio') == 'description', (
            'Check that when you PATCH request `/api/v1/users/me/` you change the data'
        )
        client_user = auth_client(moderator)
        response = client_user.patch('/api/v1/users/me/', data={'first_name': 'NewTest'})
        test_moderator = get_user_model().objects.get(username=moderator.username)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/users/me/` with authorization token returns status 200'
        )
        assert test_moderator.first_name == 'NewTest', (
            'Check that when you PATCH request `/api/v1/users/me/` you change the data'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_02_users_me_patch_user(self, user_client):
        data = {
            'first_name': 'New user first name',
            'last_name': 'New user last name',
            'bio': 'new user bio',
        }
        response = user_client.patch('/api/v1/users/me/', data=data)
        assert response.status_code == 200, (
            'Check that on a PATCH request to `/api/v1/users/me/`, '
            'a user with the user role can change their data, and a status of 200 is returned'
        )

        data = {
            'role': 'admin'
        }
        response = user_client.patch('/api/v1/users/me/', data=data)
        response_json = response.json()
        assert response_json.get('role') == 'user', (
            'Check that on a PATCH request to `/api/v1/users/me/`, '
            'a user with the user role cannot change their role'
        )
