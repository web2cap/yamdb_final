from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .messages import MESSAGES
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для Users."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "bio",
        )
        lookup_field = "username"


class UserSignupSerializer(serializers.ModelSerializer):
    "Сериалайзер для самостоятельной регистрации пользователей."

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(MESSAGES["username_invalid"])
        return value

    class Meta:
        model = User
        fields = ("username", "email")


class UserConfirmCodeSerializer(serializers.Serializer):
    "Сериалайзер для проверки username с кодом подтверждения."
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=64, required=True)

    def validate(self, data):
        """Проверка соответстствия кода логину."""
        user = get_object_or_404(User, username=data["username"])
        if user.confirmation_code == data["confirmation_code"]:
            return data
        raise serializers.ValidationError(MESSAGES["username_or_code_invalid"])


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Category."""

    class Meta:
        model = Category
        exclude = ("id",)
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Genre."""

    class Meta:
        model = Genre
        fields = ("name", "slug")
        lookup_field = "slug"


class TitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Title."""

    genre = serializers.SlugRelatedField(
        slug_field="slug", many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = "__all__"


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Title при действии 'retrieve', 'list.'"""

    rating = serializers.IntegerField(
        source="reviews__score__avg", read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for model Review."""

    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        exclude = ("title",)
        model = Review
        read_only_fields = ("id", "title", "pub_date")

    @staticmethod
    def check_only_one_review(review):
        if review:
            raise serializers.ValidationError(MESSAGES["duplication_review"])


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for model Comment."""

    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        exclude = ("review",)
        model = Comment
        read_only_fields = ("id", "review", "pub_date")
