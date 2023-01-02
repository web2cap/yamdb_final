import pytest

from .common import (auth_client, create_reviews, create_titles,
                     create_users_api)


class Test05ReviewAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_review_not_auth(self, client, admin_client):
        titles, _, _ = create_titles(admin_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        assert response.status_code != 404, (
            'Page `/API/V1/Titles/{Title_id}/Reviews/` Not found, check this address in *urls.py *'
        )
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` '
            'Without an authorization token, status 200 returns'
        )

    def create_review(self, client_user, title_id, text, score):
        data = {'text': text, 'score': score}
        response = client_user.post(f'/api/v1/titles/{title_id}/reviews/', data=data)
        assert response.status_code == 201, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'With the correct data returns status 201, API is available for any authenticated user '
        )
        return response

    @pytest.mark.django_db(transaction=True)
    def test_02_review_admin(self, admin_client, admin):
        titles, _, _ = create_titles(admin_client)
        user, moderator = create_users_api(admin_client)
        client_user = auth_client(user)
        client_moderator = auth_client(moderator)
        data = {}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'With incorrect data returns status 400 '
        )
        self.create_review(admin_client, titles[0]["id"], 'qwerty', 5)
        data = {
            'text': 'Hat',
            'score': 1
        }
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        code = 400
        assert response.status_code == code, (
            'Check that when posting on `/API/V1/Titles/{Title_id}/Reviews/` '
            'You can not add a second review to the same work, and returns'
            f'Status {code} '
        )
        try:
            from reviews.models import Review, Title
        except Exception as e:
            assert False, (
                'It was not possible to import models from the Reviews application.'
                f'Error: {e} '
            )
        from django.db.utils import IntegrityError
        title = Title.objects.get(pk=titles[0]["id"])
        review = None
        try:
            review = Review.objects.create(
                text='Text of the second review ',
                score='5',
                author=admin,
                title=title
            )
        except IntegrityError:
            pass

        assert review is None, (
            'Check that through a direct request to Django ORM '
            'You can not add a second review to the same work.'
            'This check is carried out at the model level. '
        )
        response = admin_client.put(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        code = 405
        assert response.status_code == code, (
            'Check that Put request for `/API/V1/Titles/{Title_id}/Reviews/` '
            'not allowed, and returns'
            f'Status {code} '
        )
        self.create_review(client_user, titles[0]["id"], 'Well', 3)
        self.create_review(client_moderator, titles[0]["id"], 'Will go under the beer', 4)

        self.create_review(admin_client, titles[1]["id"], 'Finally about nothing', 2)
        self.create_review(client_user, titles[1]["id"], 'Normaldes', 4)
        response = self.create_review(client_moderator, titles[1]["id"], 'So yourself', 3)

        assert type(response.json().get('id')) == int, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'Return the data of the created object.The value of `ID` is not or is not the whole. '
        )

        data = {'text': 'kjdfg', 'score': 4}
        response = admin_client.post('/api/v1/titles/999/reviews/', data=data)
        assert response.status_code == 404, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'With non -existing Title_id returns status 404. '
        )
        data = {'text': 'аывв', 'score': 11}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'with `score` more than 10 returns status 400. '
        )
        data = {'text': 'аывв', 'score': 0}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'with `score` less than 1 returns status 400. '
        )
        data = {'text': 'аывв', 'score': 2}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/` '
            'Status 400 is returned to the already left review for the object. '
        )

        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        assert response.status_code == 200, (
            'Check that with a GET request `/API/V1/Titles/{Title_id}/Reviews/` Returns status 200 '
        )
        data = response.json()
        assert 'count' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'No parameter is found `Count` '
        )
        assert 'next' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'Or from the Naun setting `next` '
        )
        assert 'previous' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'No parameter `previous` '
        )
        assert 'results' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The `Results` parameter was not found'
        )
        assert data['count'] == 3, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The value of the `Count` parameter is not correct '
        )
        assert type(data['results']) == list, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The type of parameter `Results must be a list '
        )
        assert len(data['results']) == 3, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The value of the `Results parameter is not correct'
        )

        if data['results'][0].get('text') == 'qwerty':
            review = data['results'][0]
        elif data['results'][1].get('text') == 'qwerty':
            review = data['results'][1]
        elif data['results'][2].get('text') == 'qwerty':
            review = data['results'][2]
        else:
            assert False, (
                'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` '
                'Return data with pagination.The value of the `Results parameter is wrong,'
                '`Text` was not found or not preserved during a post request. '
            )

        assert review.get('score') == 5, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The value of the `Results parameter is wrong,` score` was not found or not preserved during a post request'
        )
        assert review.get('author') == admin.username, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The value of the `Results parameter is wrong,` author` was not found or not preserved during a post request.'
        )
        assert review.get('pub_date'), (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The value of the `Results parameter is wrong,` pub_date` was not found.'
        )
        assert type(review.get('id')) == int, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/` Return data with pagination.'
            'The value of the `Results parameter is wrong, the value of` id` is not or is not the whole.'
        )

        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('rating') == 4, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` '
            'With reviews, the value of `rating`  returns correctly')
        response = admin_client.get(f'/api/v1/titles/{titles[1]["id"]}/')
        data = response.json()
        assert data.get('rating') == 3, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` '
            'With reviews, the value of `rating`  returns correctly'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_review_detail(self, client, admin_client, admin):
        reviews, titles, user, moderator = create_reviews(admin_client, admin)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code != 404, (
            'Page `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` Not found, check this address in *urls.PY *'
        )
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Without an authorization token, status 200 returns'
        )
        data = response.json()
        assert type(data.get('id')) == int, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return the object data.The value of `ID` is not or is not the whole. '
        )
        assert data.get('score') == reviews[0]['score'], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return the object data.The value of `score` is wrong. '
        )
        assert data.get('text') == reviews[0]['text'], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return the object data.The value of `text` is wrong. '
        )
        assert data.get('author') == reviews[0]['author'], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return the object data.The value of `author` is wrong. '
        )

        review_text = 'Top finally !!'
        data = {
            'text': review_text,
            'score': 10
        }
        response = admin_client.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'возвращается статус 200'
        )
        data = response.json()
        assert data.get('text') == review_text, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return the object data.The value of `text` changed. '
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Without an authorization token, status 200 returns'
        )
        data = response.json()
        assert data.get('text') == review_text, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Change the value `text`. '
        )
        assert data.get('score') == 10, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Change the value of `score`. '
        )

        client_user = auth_client(user)
        data = {
            'text': 'fgf',
            'score': 1
        }
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[2]["id"]}/', data=data)
        assert response.status_code == 403, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'From an ordinary user, when trying to change his review, status 403 returns not his review.'
        )

        data = {
            'text': 'jdfk',
            'score': 7
        }
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'The status of 200 returns'
        )
        data = response.json()
        assert data.get('text') == 'jdfk', (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return the object data.The value of `text` changed. '
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('rating') == 7, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/` '
            'With reviews, the value of `rating` returns correctly'
        )

        client_moderator = auth_client(moderator)
        response = client_moderator.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/')
        assert response.status_code == 204, (
            'Check that when the Delete request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` '
            'Return status 204 '
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        test_data = response.json()['results']
        assert len(test_data) == len(reviews) - 1, (
            'Check that when the Delete request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/` Delete the object '
        )

    def check_permissions(self, user, user_name, reviews, titles):
        client_user = auth_client(user)
        data = {'text': 'jdfk', 'score': 7}
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/', data=data)
        assert response.status_code == 403, (
            f'Check that with a Patch request `/API/V1/Titles/{{Title_id}}/Reviews/{{Review_id}}/` '
            f'With the authorization token {user_name} returns status 403 '
        )
        response = client_user.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code == 403, (
            f'Проверьте, что при DELETE запросе `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            f'с токеном авторизации {user_name} возвращается статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_reviews_check_permission(self, client, admin_client, admin):
        reviews, titles, user, moderator = create_reviews(admin_client, admin)
        data = {'text': 'jdfk', 'score': 7}
        response = client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 401, (
            'Check that when posting `/API/V1/Titles/{{Title_id}}/Reviews/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/', data=data)
        assert response.status_code == 401, (
            'Check that with a Patch request `/API/V1/Titles/{{Title_id}}/Reviews/{{Review_id}}/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/')
        assert response.status_code == 401, (
            'Check that when the Delete request is `/API/V1/Titles/{{Title_id}}/Reviews/{{Review_id}}/` '
            'Without an authorization token, status 401 returns'
        )
        self.check_permissions(user, 'ordinary user', reviews, titles)
