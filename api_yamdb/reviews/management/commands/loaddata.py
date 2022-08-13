import csv

import django.db.utils
from django.core.management.base import BaseCommand

from reviews.models import Genre, Category, Title, Review, Comment
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("static/data/users.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                User.objects.get_or_create(
                    pk=row["id"],
                    defaults={
                        "username": row["username"],
                        "email": row["email"],
                        "role": row["role"],
                        "bio": row["bio"],
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                    },
                )

        with open("static/data/genre.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Genre.objects.get_or_create(
                    pk=row["id"],
                    defaults={
                        "name": row["name"],
                        "slug": row["slug"],
                    },
                )

        with open(
            "static/data/category.csv", "r", encoding="utf-8"
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Category.objects.get_or_create(
                    pk=row["id"],
                    defaults={
                        "name": row["name"],
                        "slug": row["slug"],
                    },
                )

        with open("static/data/titles.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Title.objects.get_or_create(
                    pk=row["id"],
                    defaults={
                        "name": row["name"],
                        "year": row["year"],
                        "category": Category.objects.get(pk=row["category"]),
                    },
                )

        with open(
            "static/data/genre_title.csv", "r", encoding="utf-8"
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    Genre.objects.get(pk=row["genre_id"]).titles.add(
                        row["title_id"]
                    )
                except django.db.utils.IntegrityError:
                    continue

        with open("static/data/review.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Review.objects.get_or_create(
                    pk=row["id"],
                    defaults={
                        "text": row["text"],
                        "author": User.objects.get(pk=row["author"]),
                        "score": row["score"],
                        "pub_date": row["pub_date"],
                        "title": Title.objects.get(pk=row["title_id"]),
                    },
                )

        with open(
            "static/data/comments.csv", "r", encoding="utf-8"
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Comment.objects.get_or_create(
                    pk=row["id"],
                    defaults={
                        "review": Review.objects.get(pk=row["review_id"]),
                        "author": User.objects.get(pk=row["author"]),
                        "text": row["text"],
                        "pub_date": row["pub_date"],
                    },
                )
