import pytest

from .common import (auth_client, create_categories, create_genre,
                     create_titles, create_users_api)


class Test04TitleAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_title_not_auth(self, client):
        response = client.get('/api/v1/titles/')
        assert response.status_code != 404, (
            'Page `/API/V1/Titles/` Not found, check this address in *urls.py *'
        )
        assert response.status_code == 200, (
            'Check that with a GET request `/API/V1/Titles/` Without an authorization token, status 200 returns the status'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_title_admin(self, admin_client):
        genres = create_genre(admin_client)
        categories = create_categories(admin_client)
        data = {}
        response = admin_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 400, (
            'Check that when post `/API/V1/Titles/` with non -correct data returns status 400 '
        )
        data = {'name': 'Turn there', 'year': 2000, 'genre': [genres[0]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Cool peak'}
        response = admin_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 201, (
            'Check that when post `/API/V1/Titles/` with the correct data returns status 201 '
        )
        data = {'name': 'Project', 'year': 2020, 'genre': [genres[2]['slug']], 'category': categories[1]['slug'],
                'description': 'The main drama of the year'}
        response = admin_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 201, (
            'Check that when post `/API/V1/Titles/` with the correct data returns status 201 '
        )
        assert type(response.json().get('id')) == int, (
            'Check that when posting `/API/V1/Titles/` Return the data of the created object.'
            'The value of `ID` is not or is not the whole. '
        )
        response = admin_client.get('/api/v1/titles/')
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/` returns the status of 200 '
        )
        data = response.json()
        assert 'count' in data, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'No parameter is found `Count` '
        )
        assert 'next' in data, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'Or from the Naun setting `next` '
        )
        assert 'previous' in data, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'No parameter `previous` '
        )
        assert 'results' in data, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The `Results` parameter was not found'
        )
        assert data['count'] == 2, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Count` parameter is not correct '
        )
        assert type(data['results']) == list, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The type of parameter `Results must be a list '
        )
        assert len(data['results']) == 2, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is not correct'
        )
        if data['results'][0].get('name') == 'Turn there':
            title = data['results'][0]
        elif data['results'][1].get('name') == 'Turn there':
            title = data['results'][1]
        else:
            assert False, (
                'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
                'The value of the `Results` parameter is wrong,` name` was not found or not preserved during a post request.'
            )

        assert title.get('rating') is None, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is wrong,` rating` without reviews should be `none`'
        )
        assert title.get('category') == categories[0], (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is wrong, the value of` Category` is wrong'
            'or was not preserved during the Post. '
        )
        assert genres[0] in title.get('genre', []) and genres[1] in title.get('genre', []), (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is wrong, the value of` genre` is wrong'
            'or was not preserved during the Post. '
        )
        assert title.get('year') == 2000, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is wrong, the value of` year` is wrong'
            'or was not preserved during the Post. '
        )
        assert title.get('description') == 'Cool peak', (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is wrong, the value of` description` is wrong'
            'or was not preserved during the Post. '
        )
        assert type(title.get('id')) == int, (
            'Check that when a GET request is `/API/V1/Titles/` Return data with pagination.'
            'The value of the `Results` parameter is wrong, the value of` id` is not or is not the whole.'
        )
        data = {'name': 'Turn', 'year': 2020, 'genre': [genres[1]['slug']],
                'category': categories[1]['slug'], 'description': 'Cool peak'}
        admin_client.post('/api/v1/titles/', data=data)
        response = admin_client.get(f'/api/v1/titles/?genre={genres[1]["slug"]}')
        data = response.json()
        assert len(data['results']) == 2, (
            'Check that when a GET request `/API/V1/Titles/` is filtered according to the `genre` parameter` SLUG` genre '
        )
        response = admin_client.get(f'/api/v1/titles/?category={categories[0]["slug"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that when a GET request `/API/V1/Titles/` is filtered according to the `Category` parameter` SLUG` category '
        )
        response = admin_client.get('/api/v1/titles/?year=2000')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that when a GET request `/API/V1/Titles/` is filtered according to the `year` parameter of the year '
        )
        response = admin_client.get('/api/v1/titles/?name=Turn')
        data = response.json()
        assert len(data['results']) == 2, (
            'Check that when a GET request `/API/V1/Titles/` is filtered according to the `name` parameter of the name '
        )
        invalid_data = {
            'name': 'Turn', 'year': 'There are six boys', 'genre': [genres[1]['slug']],
            'category': categories[1]['slug'], 'description': 'Cool peak'
        }
        response = admin_client.post('/api/v1/titles/', data=invalid_data)
        code = 400
        assert response.status_code == code, (
            'Check that during the Post `/API/V1/Titles/`, the YEAR field is valid'
            'and when transmitting incorrect value, status 400 is returned'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_titles_detail(self, client, admin_client):
        titles, categories, genres = create_titles(admin_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code != 404, (
            'Page `/API/V1/Titles/{Title_id}/` Not found, check this address in *urls.py *'
        )
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` '
            'Without an authorization token, status 200 returns'
        )
        data = response.json()
        assert type(data.get('id')) == int, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` Return the object data.'
            'The value of `ID` is not or is not the whole. '
        )
        assert data.get('category') == categories[0], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` Return the object data.'
            'The value of `Category` is wrong. '
        )
        assert data.get('name') == titles[0]['name'], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` Return the object data.'
            'The value of `name` is wrong. '
        )
        data = {
            'name': 'New name',
            'category': categories[1]['slug']
        }
        response = admin_client.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/` Status 200 returns'
        )
        data = response.json()
        assert data.get('name') == 'New name', (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/` Return the object data.'
            'Meaning `Name` modified. '
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` '
            'Without an authorization token, status 200 returns'
        )
        data = response.json()
        assert data.get('category') == categories[1], (
            'Check that when the Patch request is `/API/V1/Titles/{Title_id}/` Change the value `Category`. '
        )
        assert data.get('name') == 'New name', (
            'Check that when the Patch request is `/API/V1/Titles/{Title_id}/` Change the value `name`. '
        )

        response = admin_client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 204, (
            'Check what is `/API/V1/Titles/{Title_id}/` Return Status 204 '
        )
        response = admin_client.get('/api/v1/titles/')
        test_data = response.json()['results']
        assert len(test_data) == len(titles) - 1, (
            'Check that when the Delete request is `/API/V1/Titles/{Title_id}/` Delete the object '
        )

    def check_permissions(self, user, user_name, titles, categories, genres):
        client_user = auth_client(user)
        data = {'name': 'Chudo Yuo', 'year': 1999, 'genre': [genres[2]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Boom'}
        response = client_user.post('/api/v1/titles/', data=data)
        assert response.status_code == 403, (
            f'Check that when posting `/API/V1/Titles/` '
            f'With the authorization token {user_name} returns status 403 '
        )
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 403, (
            f'Check that when the PATCH request is `/API/V1/Titles/{{title_id}}/` '
            f'With the authorization token {user_name} returns status 403 '
        )
        response = client_user.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 403, (
            f'Check that when the Delete request is `/API/V1/Titles/{{title_id}}/` '
            f'With the authorization token {user_name} returns status 403 '
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_titles_check_permission(self, client, admin_client):
        titles, categories, genres = create_titles(admin_client)
        data = {'name': 'Chudo Yuo', 'year': 1999, 'genre': [genres[2]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Boom'}
        response = client.post('/api/v1/titles/', data=data)
        assert response.status_code == 401, (
            'Check that when posting `/API/V1/Titles/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 401, (
            'Check that when the PATCH request is `/API/V1/Titles/{{Title_id}}/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 401, (
            'Check that when the Delete request is `/API/V1/Titles/{{Title_id}}/` '
            'Without an authorization token, status 401 returns'
        )
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'ordinary user', titles, categories, genres)
        self.check_permissions(moderator, 'moderator', titles, categories, genres)
