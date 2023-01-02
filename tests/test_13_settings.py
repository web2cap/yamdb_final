from api_yamdb import settings


class TestSettings:

    def test_settings(self):
        
        accepted_db_engine = (
            'django.db.backends.postgresql',
            'django.db.backends.postgresql_psycopg2'
        )
        assert not settings.DEBUG, 'Check that DEBUG is disabled in Django settings'
        assert settings.DATABASES['default']['ENGINE'] in accepted_db_engine, (
            'Check you are using postgresql database'
        )
