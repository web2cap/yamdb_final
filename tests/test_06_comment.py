import pytest

from .common import auth_client, create_comments, create_reviews


class Test06CommentAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_comment_not_auth(self, client, admin_client, admin):
        reviews, titles, _, _ = create_reviews(admin_client, admin)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/')
        assert response.status_code != 404, (
            'Page `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comments/` '
            'Not found, check this address in *urls.py *'
        )
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Without an authorization token, status 200 returns'
        )

    def create_comment(self, client_user, title_id, review_id, text):
        data = {'text': text}
        response = client_user.post(f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/', data=data)
        assert response.status_code == 201, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'With the correct data returns status 201, API is available for any authenticated user '
        )
        return response

    @pytest.mark.django_db(transaction=True)
    def test_02_comment(self, admin_client, admin):
        reviews, titles, user, moderator = create_reviews(admin_client, admin)
        client_user = auth_client(user)
        client_moderator = auth_client(moderator)
        data = {}
        response = admin_client.post(
            f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/', data=data
        )
        assert response.status_code == 400, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'With incorrect data returns status 400 '
        )
        self.create_comment(admin_client, titles[0]["id"], reviews[0]["id"], 'qwerty')
        self.create_comment(client_user, titles[0]["id"], reviews[0]["id"], 'qwerty123')
        self.create_comment(client_moderator, titles[0]["id"], reviews[0]["id"], 'qwerty321')

        self.create_comment(admin_client, titles[0]["id"], reviews[1]["id"], 'qwerty432')
        self.create_comment(client_user, titles[0]["id"], reviews[1]["id"], 'qwerty534')
        response = self.create_comment(client_moderator, titles[0]["id"], reviews[1]["id"], 'qwerty231')

        assert type(response.json().get('id')) == int, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return the data of the created object.The value of `ID` is not or is not the whole. '
        )

        data = {'text': 'kjdfg'}
        response = admin_client.post('/api/v1/titles/999/reviews/999/comments/', data=data)
        assert response.status_code == 404, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'With non -existing Title_id or Review_id returns status 404. '
        )
        data = {'text': 'аывв'}
        response = admin_client.post(
            f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/', data=data
        )
        assert response.status_code == 201, (
            'Check that when posting `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'You can leave a few comments on the review. '
        )

        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/')
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'returns status 200 '
        )
        data = response.json()
        assert 'count' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.No parameter is found `Count` '
        )
        assert 'next' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.No parameter `next` '
        )
        assert 'previous' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.No parameter `previous` '
        )
        assert 'results' in data, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.The `Results` parameter was not found'
        )
        assert data['count'] == 4, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.The value of the `Count` parameter is not correct '
        )
        assert type(data['results']) == list, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.The type of parameter `Results must be a list '
        )
        assert len(data['results']) == 4, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.The value of the `Results parameter is not correct'
        )

        comment = None
        for item in data['results']:
            if item.get('text') == 'qwerty':
                comment = item
        assert comment, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.The value of the `Results parameter is wrong,'
            '`Text` was not found or not preserved during a post request. '
        )
        assert comment.get('author') == admin.username, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.'
            'The value of the `Results parameter is wrong,` author` was not found or not preserved during a post request.'
        )
        assert comment.get('pub_date'), (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            ' Return data with pagination.The value of the `Results parameter is wrong,` pub_date` was not found.'
        )
        assert type(comment.get('id')) == int, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/` '
            'Return data with pagination.'
            'The value of the `Results parameter is wrong, the value of` id` is not or is not the whole.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_review_detail(self, client, admin_client, admin):
        comments, reviews, titles, user, moderator = create_comments(admin_client, admin)
        pre_url = f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/'
        response = client.get(f'{pre_url}{comments[0]["id"]}/')
        assert response.status_code != 404, (
            'Page `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comments/{COMMENT_ID}/` '
            'Not found, check this address in *urls.py *'
        )
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Without an authorization token, status 200 returns'
        )
        data = response.json()
        assert type(data.get('id')) == int, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Return the object data.The value of `ID` is not or is not the whole. '
        )
        assert data.get('text') == reviews[0]['text'], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'возвращаете данные объекта. Значение `text` неправильное.'
        )
        assert data.get('author') == reviews[0]['author'], (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Return the object data.The value of `author` is wrong. '
        )

        data = {'text': 'rewq'}
        response = admin_client.patch(f'{pre_url}{comments[0]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'The status of 200 returns'
        )
        data = response.json()
        assert data.get('text') == 'rewq', (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Return the object data.The value of `text` changed. '
        )
        response = admin_client.get(f'{pre_url}{comments[0]["id"]}/')
        assert response.status_code == 200, (
            'Check that when a GET request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Without an authorization token, status 200 returns'
        )
        data = response.json()
        assert data.get('text') == 'rewq', (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Change the value `text`. '
        )

        client_user = auth_client(user)
        data = {'text': 'fgf'}
        response = client_user.patch(f'{pre_url}{comments[2]["id"]}/', data=data)
        assert response.status_code == 403, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'From an ordinary user, when trying to change his review, status 403 returns not his review.'
        )

        data = {'text': 'jdfk'}
        response = client_user.patch(f'{pre_url}{comments[1]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'The status of 200 returns'
        )
        data = response.json()
        assert data.get('text') == 'jdfk', (
            'Check that with a Patch request `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Return the object data.The value of `text` changed. '
        )

        client_moderator = auth_client(moderator)
        response = client_moderator.delete(f'{pre_url}{comments[1]["id"]}/')
        assert response.status_code == 204, (
            'Check that when the Delete request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Return status 204 '
        )
        response = admin_client.get(f'{pre_url}')
        test_data = response.json()['results']
        assert len(test_data) == len(comments) - 1, (
            'Check that when the Delete request is `/API/V1/Titles/{Title_id}/Reviews/{Review_id}/Comment/{Comment_id}/` '
            'Delete the object '
        )

    def check_permissions(self, user, user_name, pre_url):
        client_user = auth_client(user)
        data = {'text': 'jdfk'}
        response = client_user.patch(pre_url, data=data)
        assert response.status_code == 403, (
            f'Check that with a Patch request `/API/V1/Titles/{{Title_id}}/Reviews/{{Review_id}}/` '
            f'With the authorization token {user_name} returns status 403 '
        )
        response = client_user.delete(pre_url)
        assert response.status_code == 403, (
            f'Check that when the Delete request is `/API/V1/Titles/{{Title_id}}/Reviews/{{Review_id}}/` '
            f'With the authorization token {user_name} returns status 403 '
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_comment_check_permission(self, client, admin_client, admin):
        comments, reviews, titles, user, moderator = create_comments(admin_client, admin)
        pre_url = f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/'
        data = {'text': 'jdfk'}
        response = client.post(f'{pre_url}', data=data)
        assert response.status_code == 401, (
            'Check that when posting `/API/V1/Titles/{{Title_id}}/Reviews/{{Review_id}}/comments/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.patch(f'{pre_url}{comments[1]["id"]}/', data=data)
        assert response.status_code == 401, (
            'Check what for the Patch request '
            '`/api/v1/titles/{{titleId}}/reviews/{{reviewId}}/comments/{{commentId}}/` '
            'Without an authorization token, status 401 returns'
        )
        response = client.delete(f'{pre_url}{comments[1]["id"]}/')
        assert response.status_code == 401, (
            'Check what for the Delete request '
            '`/api/v1/titles/{{titleId}}/reviews/{{reviewId}}/comments/{{commentId}}/` '
            'Without an authorization token, status 401 returns'
        )
        self.check_permissions(user, 'ordinary user', f'{pre_url}{comments[2]["id"]}/')
