from django.db import models
from users.models import User

from .validators import validator_year


class CreatedModel(models.Model):
    """Abstract model. Adds the publication date on creation."""

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date and time of publication",
        help_text="Automatically set when publishing",
    )

    class Meta:
        abstract = True


class Genre(models.Model):
    """Model Genre for Title."""

    name = models.CharField(
        verbose_name="Genre",
        help_text="Name of the genre of the work",
        max_length=256,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Genre address",
        help_text="The unique address of the genre, part of the URL"
        "(for example, for the genre a fantasy slug can be fantastic).",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ["name"]

    def __str__(self):
        return self.slug


class Category(models.Model):
    """Model Category for Title."""

    name = models.CharField(
        verbose_name="Category",
        help_text="Name of the category of the work",
        max_length=256,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Category address",
        help_text="The unique address of the category, part of the URL"
        "(for example, for category movies slug could be films).",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Model Title."""

    name = models.CharField(
        verbose_name="Product",
        help_text="Product name",
        max_length=256,
    )
    year = models.PositiveIntegerField(
        verbose_name="Year",
        help_text="Year of creation of the product",
        validators=(validator_year,),
    )
    rating = models.IntegerField(
        verbose_name="Product Rating",
        help_text="Product rating based on user reviews",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Brief description of the work",
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Genre",
        help_text="Genre",
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Category",
        help_text="Name of the category of the work",
        related_name="titles",
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name", "year"]

    def __str__(self):
        return self.name


class Review(CreatedModel):
    """Model Review for Title."""

    SCORE_CHOICES = ((s, s) for s in range(1, 11))
    title = models.ForeignKey(
        Title,
        verbose_name="Product",
        help_text="The name of the product for which the review",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name="Text",
        help_text="Feedback text",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Autor",
        help_text="Review autor",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    score = models.IntegerField(
        verbose_name="Rating",
        help_text="Rating works from 1 to 10",
        choices=SCORE_CHOICES,
    )

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-pub_date"]
        unique_together = ["author", "title"]

    def __str__(self):
        return self.text[:30]


class Comment(CreatedModel):
    """Model Comments for Review."""

    review = models.ForeignKey(
        Review,
        verbose_name="Review",
        help_text="The review for which the comment was written",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name="Text",
        help_text="Feedback text",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Author",
        help_text="Comment author",
        related_name="comments",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]
