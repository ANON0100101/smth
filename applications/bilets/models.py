import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Ticket(models.Model):
    """
        Это моделька Тикета
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField('Название', max_length=70)
    image = models.ImageField('Изображение', upload_to='images')
    location = models.CharField('Локация', max_length=40)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    total_ticket = models.PositiveSmallIntegerField('Количества билетов')
    date = models.DateTimeField('Дата')
    description = models.TextField('Описание')
    count_views = models.PositiveIntegerField('Количество просмотров', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def decrease_total_ticket(self):
        if self.total_ticket > 0:
            self.total_ticket -= 1
            self.save(update_fields=['total_ticket'])

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.owner} -> {self.post.title}'


class Like(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='likes'
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='likes'
    )
    is_like = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.owner} liked - {self.post.title}'


class Favorite(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites'
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='favorites'
    )
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.owner} liked - {self.post.title}'


class Rating(models.Model):
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='ratings')
    post = models.ForeignKey(Ticket,
                             on_delete=models.CASCADE,
                             related_name='ratings')
    rating = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ], blank=True, null=True)

    def __str__(self):
        return f'{self.owner} --> {self.post.title}'


@receiver(post_save, sender=Ticket)
def my_handler(sender, instance, created, **kwargs):
    if created:
        print('CREATED')


class Order(models.Model):
    name = models.CharField(max_length=70)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='orders')
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=40, blank=True)

    def create_activation_code(self):
        import uuid
        code = str(uuid.uuid4())
        self.activation_code = code
        self.save()

    def __str__(self):
        return f"Order {self.pk} by {self.user.username}"

