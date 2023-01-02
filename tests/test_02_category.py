import pytest

from .common import auth_client, create_categories, create_users_api


class Test02CategoryAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_category_not_auth(self, client):
        response = client.get('/api/v1/categories/')
        assert response.status_code != 404, (
            'Page `/api/v1/categories/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/categories/` without an authorization token returns status 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_category_admin(self, admin_client):
        data = {}
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 400, (
            'Check that when post ``/API/V1/Categories/`With the wrong data, status 400 returns'
        )
        data = {
            'name': 'Фильм',
            'slug': 'films'
        }
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 201, (
            'Check that when post `/API/V1/Categories/` with the correct data returns status 201'
        )
        data = {
            'name': 'Новые фильмы',
            'slug': 'films'
        }
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 400, (
            'Check that when post `/API/V1/Categories/` You cannot create 2 categories with the same `SLUG`'
        )
        data = {
            'name': 'Books',
            'slug': 'books'
        }
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 201, (
            'Check that when post `/API/V1/Categories/` with the correct data returns status 201'
        )
        response = admin_client.get('/api/v1/categories/')
        assert response.status_code == 200, (
            'Check that with a GET request `/API/V1/Categories/` Returns Status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'Not found parametr: `count`'
        )
        assert 'next' in data, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'Not found parametr: `next`'
        )
        assert 'previous' in data, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'Not found parametr: `previous`'
        )
        assert 'results' in data, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'Not found parametr: `results`'
        )
        assert data['count'] == 2, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'The value of the parameter is not correct'
        )
        assert type(data['results']) == list, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'The type of parameter `Results must be a list'
        )
        assert len(data['results']) == 2, (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'The value of the `Results` parameter is not correct'
        )
        assert {'name': 'Books', 'slug': 'books'} in data['results'], (
            'Check that when a GET request is `/API/V1/Categories/` Return data with pagination.'
            'The value of the `Results` parameter is not correct'
        )
        response = admin_client.get('/api/v1/categories/?search=Books')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that when a GET request `/API/V1/Categories/` is filtered according to the Search parameter of the name of the category'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_category_delete_admin(self, admin_client):
        create_categories(admin_client)
        response = admin_client.delete('/api/v1/categories/books/')
        assert response.status_code == 204, (
            'Check that when the Delete request is `/API/V1/Categories/{Slug}/` Return Status 204'
        )
        response = admin_client.get('/api/v1/categories/')
        test_data = response.json()['results']
        assert len(test_data) == 1, (
            'Check that when the Delete request is `/API/V1/Categories/{Slug}/` Delete the category'
        )
        response = admin_client.get('/api/v1/categories/books/')
        code = 405
        assert response.status_code == code, (
            'Check that when a GET request is `/API/V1/Categories/{Slug}/`'
            f'Return the status{code}'
        )
        response = admin_client.patch('/api/v1/categories/books/')
        assert response.status_code == code, (
            'Check that with the Patch request `/api/v1/categories/{slug}/` '
            f'Return the status {code}'
        )

    def check_permissions(self, user, user_name, categories):
        client_user = auth_client(user)
        data = {
            'name': 'Music',
            'slug': 'music'
        }
        response = client_user.post('/api/v1/categories/', data=data)
        assert response.status_code == 403, (
            f'Check that when POST request `/api/v1/categories/` '
            f'With the authorization token {user_name} returns status 403'
        )
        response = client_user.delete(f'/api/v1/categories/{categories[0]["slug"]}/')
        assert response.status_code == 403, (
            f'Check that when the Delete request is `/API/V1/Categories/{{Slug}}/`'
            f'With the authorization token {user_name} returns status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_category_check_permission_admin(self, client, admin_client):
        categories = create_categories(admin_client)
        data = {
            'name': 'Music',
            'slug': 'music'
        }
        response = client.post('/api/v1/categories/', data=data)
        assert response.status_code == 401, (
            'Check that when post `/API/V1/Categories/`'
            'Without an authorization token, status 401 returns'
        )
        response = client.delete(f'/api/v1/categories/{categories[0]["slug"]}/')
        assert response.status_code == 401, (
            'Check that when the Delete request is `/API/V1/Categories/{{Slug}}/`'
            'Without an authorization token, status 401 returns'
        )
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'regular user', categories)
        self.check_permissions(moderator, 'moderator', categories)

    @pytest.mark.django_db(transaction=True)
    def test_05_category_create_user(self, user_client):
        url = '/api/v1/categories/'
        data = {
            'name': 'All different',
            'slug': 'something'
        }
        response = user_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when posting on `{url}`, the creation of categories is not available for'
            'user with the role of user'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_category_create_moderator(self, moderator_client):
        url = '/api/v1/categories/'
        data = {
            'name': 'All different',
            'slug': 'something'
        }
        response = moderator_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when posting on `{url}`, the creation of categories is not available for'
            f'user with the role of Moderator'
        )
