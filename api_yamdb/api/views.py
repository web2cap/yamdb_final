from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitlesFilter
from .messages import MESSAGES
from .mixins import ListCreateDestroyViewSet
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReadOnlyTitleSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserConfirmCodeSerializer,
    UserSerializer,
    UserSignupSerializer,
)
from .permissions import (
    AuthorAdminModeratorOrReadOnly,
    MeOrAdmin,
    PostOnlyNoCreate,
    RoleAdminrOrReadOnly,
)

EMAIL_NOREPLAY_ADDRESS = getattr(settings, "EMAIL_NOREPLAY_ADDRESS", None)


class AuthViewSet(viewsets.ModelViewSet):
    """Получение токена авторизации JWT в ответ на POST запрос, на адрес
    /token. POST на корневой эндпоитн и другие типы запросов запрещены
    пермишенном."""

    permission_classes = (PostOnlyNoCreate,)

    @action(detail=False, methods=["post"])
    def token(self, request):
        """Получение токена по username и confirmation_code."""

        serializer = UserConfirmCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, username=serializer.data["username"]
            )
            access_token = str(AccessToken.for_user(user))
            return Response(
                {"access": access_token}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def signup(self, request):
        """Самостоятельная регистрация нового пользователя.
        Создает пользователя по запросу.
        Отправляет код подверждения пользователю на email.
        Отправляет код подверждения на email существующим пользователям."""

        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
        else:
            if (
                "username" in serializer.data
                and User.objects.filter(
                    username=serializer.data["username"],
                    email=serializer.data["email"],
                ).exists()
            ):
                self.send_mail_code(serializer.data)
                return Response(
                    {"detail": MESSAGES["mail_send"]},
                    status=status.HTTP_200_OK,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        self.send_mail_code(serializer.data)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    def send_mail_code(self, data):
        """Функция отправки кода подтверждения."""

        user = get_object_or_404(User, username=data["username"])
        result = send_mail(
            MESSAGES["mail_theme"],
            MESSAGES["mail_text"].format(user.confirmation_code),
            EMAIL_NOREPLAY_ADDRESS,
            [data["email"]],
            fail_silently=False,
        )
        return result


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet API управления пользователями.
    Запросы к экземпляру осуществляются по username.
    При обращении на /me/ пользователь дополняет/получает свою запись."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (MeOrAdmin,)
    lookup_field = "username"

    def retrieve(self, request, username=None):
        """Получение экземпляра пользователя по username.
        При запросе на /me/ возвращает авторизованного пользователя."""

        if username == "me":
            username = request.user.username
        user = get_object_or_404(self.queryset, username=username)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, username=None):
        """Обновление экземпляра пользователя по username.
        Не позволяет установить непредусмотренную роль.
        Если пользователь не админ, не позволяет сменить роль."""

        data = request.data.copy()
        if "role" in data:
            if data["role"] not in ("user", "admin", "moderator"):
                return Response(
                    {"detail": MESSAGES["wrong_role"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not request.user.is_admin:
                data.pop("role")
        serializer = UserSerializer(request.user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    def destroy(self, request, username=None):
        """Удаление пользователя.
        Не позволяет удалить самого себя при запросе на /me/."""

        if username == "me":
            return Response(
                {"detail": MESSAGES["no_delete_yourself"]},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ListCreateDestroyViewSet):
    """API для работы с моделью категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (RoleAdminrOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    """API для работы с моделью жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (RoleAdminrOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """API для работы произведений."""

    queryset = (
        Title.objects.all().annotate(Avg("reviews__score")).order_by("name")
    )
    permission_classes = (RoleAdminrOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter
    http_method_names = ["get", "post", "delete", "patch"]

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Class api for model Review."""

    serializer_class = ReviewSerializer
    permission_classes = [AuthorAdminModeratorOrReadOnly]
    http_method_names = ["get", "post", "delete", "patch"]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        review = Review.objects.filter(author=self.request.user, title=title)
        serializer.check_only_one_review(review)
        serializer.save(author=self.request.user, title=title)

        title.rating = title.reviews.all().aggregate(Avg("score"))[
            "score__avg"
        ]
        title.save()

    def perform_update(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save()

        title.rating = title.reviews.all().aggregate(Avg("score"))[
            "score__avg"
        ]
        title.save()

    def perform_destroy(self, instance):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        instance.delete()

        title.rating = title.reviews.all().aggregate(Avg("score"))[
            "score__avg"
        ]
        title.save()


class CommentViewSet(viewsets.ModelViewSet):
    """Class api for model Comment."""

    serializer_class = CommentSerializer
    permission_classes = [AuthorAdminModeratorOrReadOnly]
    http_method_names = ["get", "post", "delete", "patch"]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        review = get_object_or_404(
            Review, pk=self.kwargs.get("review_id"), title=title
        )
        return review.comments.all()

    def perform_create(self, serializer):
        get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)
