import pytest

from .common import auth_client, create_genre, create_users_api


class Test03GenreAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_genre_not_auth(self, client):
        response = client.get('/api/v1/genres/')
        assert response.status_code != 404, (
            'Page `/API/V1/Genres/` Not found, check this address in *urls.py *'
        )
        assert response.status_code == 200, (
            'Check that with a GET request `/API/V1/Genres/` Status 200 is returned without authorization token.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_genre(self, admin_client):
        data = {}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 400, (
            'Check that when post `/API/V1/Genres/` with non -correct data returns status 400 '
        )
        data = {'name': 'Horrors', 'slug': 'horror'}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 201, (
            'Check that when post `/API/V1/Genres/` with the correct data returns status 201 '
        )
        data = {'name': 'Thriller', 'slug': 'horror'}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 400, (
            'Check that when post `/API/V1/Genres/` You cannot create 2 genres with the same `SLUG` '
        )
        data = {'name': 'Comedy', 'slug': 'comedy'}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 201, (
            'Check that when post `/API/V1/Genres/` with the correct data returns status 201 '
        )
        response = admin_client.get('/api/v1/genres/')
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Genres/` returns status 200 '
        )
        data = response.json()
        assert 'count' in data, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'No parameter is found `Count` '
        )
        assert 'next' in data, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'Or from the Naun setting `next` '
        )
        assert 'previous' in data, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'No parameter `previous` '
        )
        assert 'results' in data, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'The `Results` parameter was not found'
        )
        assert data['count'] == 2, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'The value of the `Count` parameter is not correct '
        )
        assert type(data['results']) == list, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'The type of parameter `Results must be a list '
        )
        assert len(data['results']) == 2, (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'The value of the `Results parameter is not correct'
        )
        assert {'name': 'Horrors', 'slug': 'horror'} in data['results'], (
            'Check that when a GET request is `/API/V1/Genres/` Return data with pagination.'
            'The value of the `Results` parameter is not correct'
        )
        response = admin_client.get('/api/v1/genres/?search=Horrors')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that when a GET request `/API/V1/Genres/` is filtered according to the Search parameter of the name of the genre '
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_genres_delete(self, admin_client):
        genres = create_genre(admin_client)
        response = admin_client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 204, (
            'Check that when the Delete request is `/API/V1/Genres/{Slug}/` Return Status 204 '
        )
        response = admin_client.get('/api/v1/genres/')
        test_data = response.json()['results']
        assert len(test_data) == len(genres) - 1, (
            'Check what is `/API/V1/Genres/{SLUG}/` Delete the genre '
        )
        response = admin_client.get(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, (
            'Check that when a GET request is `/API/V1/Genres/{Slug}/` Return Status 405 '
        )
        response = admin_client.patch(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, (
            'Check that with a Patch request `/API/V1/Genres/{Slug}/` Return Status 405 '
        )

    def check_permissions(self, user, user_name, genres):
        client_user = auth_client(user)
        data = {
            'name': 'Action',
            'slug': 'action'
        }
        response = client_user.post('/api/v1/genres/', data=data)
        assert response.status_code == 403, (
            f'Check that when post `/API/V1/Genres/` '
            f'With the authorization token {user_name} returns status 403 '
        )
        response = client_user.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 403, (
            f'Check that when the Delete request is `/API/V1/Genres/{{Slug}}/` '
            f'With the authorization token {user_name} returns status 403 '
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_genres_check_permission(self, client, admin_client):
        genres = create_genre(admin_client)
        data = {
            'name': 'Action',
            'slug': 'action'
        }
        response = client.post('/api/v1/genres/', data=data)
        assert response.status_code == 401, (
            'Check that when post `/API/V1/Genres/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 401, (
            'Check that when the Delete request is `/API/V1/Genres/{{Slug}}/` '
            'Without an authorization token, status 401 returns'
        )
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'ordinary user', genres)
        self.check_permissions(moderator, 'moderator', genres)

    @pytest.mark.django_db(transaction=True)
    def test_05_genre_create_user(self, user_client):
        url = '/api/v1/genres/'
        data = {
            'name': 'All different',
            'slug': 'something'
        }
        response = user_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when posting on `{url}`, the creation of genres is not available for '
            f'User with the role of user '
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_genre_create_moderator(self, moderator_client):
        url = '/api/v1/genres/'
        data = {
            'name': 'All different',
            'slug': 'something'
        }
        response = moderator_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when posting on `{url}`, the creation of genres is not available for '
            f'User with the role of Moderator '
        )
