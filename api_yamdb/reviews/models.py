from django.db import models

from .validators import validator_year
from users.models import User


class CreatedModel(models.Model):
    """Abstract model. Adds the publication date on creation."""

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время публикации",
        help_text="Автоматически задается при публикации",
    )

    class Meta:
        abstract = True


class Genre(models.Model):
    """Model Genre for Title."""

    name = models.CharField(
        verbose_name="Жанр",
        help_text="Наименование жанра произведения",
        max_length=256,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Адрес жанра",
        help_text="Уникальный адрес жанра, часть URL (например, для жанра "
        "фантастики slug может быть fantastic).",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["name"]

    def __str__(self):
        return self.slug


class Category(models.Model):
    """Model Category for Title."""

    name = models.CharField(
        verbose_name="Категория",
        help_text="Наименование категории произведения",
        max_length=256,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Адрес категории",
        help_text="Уникальный адрес категории, часть URL (например, для "
        "категории фильмы slug может быть films).",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Model Title."""

    name = models.CharField(
        verbose_name="Произведение",
        help_text="Наименование произведения",
        max_length=256,
    )
    year = models.PositiveIntegerField(
        verbose_name="Год",
        help_text="Год создания произведения",
        validators=(validator_year,),
    )
    rating = models.IntegerField(
        verbose_name="Рейтинг произведения",
        help_text="Рейтинг произведения на основе отзывов пользователей",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Краткое описание произведения",
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр",
        help_text="Жанр произведения",
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        help_text="Категория произведения",
        related_name="titles",
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ["name", "year"]

    def __str__(self):
        return self.name


class Review(CreatedModel):
    """Model Review for Title."""

    SCORE_CHOICES = ((s, s) for s in range(1, 11))
    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        help_text="Наименование произведения, для которого отзыв",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст отзыва",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        help_text="Автор отзыва",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    score = models.IntegerField(
        verbose_name="Оценка",
        help_text="Оценка произведения от 1 до 10",
        choices=SCORE_CHOICES,
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-pub_date"]
        unique_together = ["author", "title"]

    def __str__(self):
        return self.text[:30]


class Comment(CreatedModel):
    """Model Comments for Review."""

    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        help_text="Отзыв, для которого написан комментарий",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст отзыва",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        help_text="Автор комментария",
        related_name="comments",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]
