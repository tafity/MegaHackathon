from PIL import Image
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, URLValidator

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# функция получения пути для сохранения фотографий, чтобы было понятно, к какому instance они относятся
def get_image_path(instance, file):
    return f'photos/{instance}/{file}'


# функция получения изображения профиля по умолчанию
def get_default_profile_image():
    return 'photos/default_profile_img.png'


def validate_size_image(file_obj):
    """ Проверка размера файла
    """
    megabyte_limit = 2
    if file_obj.size > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"Максимальный размер файла {megabyte_limit}MB")


# class OptionalSchemeURLValidator(URLValidator):
#     def __call__(self, value):
#         if '://' not in value:
#             # Validate as if it were http://
#             value = f'https://{value}'
#         super(OptionalSchemeURLValidator, self).__call__(value)


class ProfileManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('У пользователей должен быть email.')

        if not username:
            raise ValueError('У пользователей должен быть username.')

        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=self.normalize_email(email), username=username, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# class Profile(models.Model):
class Profile(AbstractBaseUser):
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Последний вход')
    username = models.CharField(max_length=150, verbose_name='Имя пользователя', unique=True)
    email = models.EmailField(max_length=254, verbose_name='Email', unique=True)
    first_name = models.CharField(max_length=150, verbose_name='Имя', blank=True, null=True)
    last_name = models.CharField(max_length=150, verbose_name='Фамилия', blank=True, null=True)
    city = models.CharField(max_length=150, verbose_name='Город', blank=True, null=True)
    date_of_birth = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    is_admin = models.BooleanField(default=False, verbose_name='Статус администратора')
    is_staff = models.BooleanField(default=False, verbose_name='Статус персонала')
    is_superuser = models.BooleanField(default=False, verbose_name='Статус суперпользователя')
    hide_email = models.BooleanField(default=True, verbose_name='Скрыть email')
    bio = models.TextField(null=True, blank=True, verbose_name='О себе')
    image = models.ImageField(
        default=get_default_profile_image,
        upload_to=get_image_path,
        verbose_name='Фотография',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'png']),
            validate_size_image,
            # OptionalSchemeURLValidator(),
        ]
    )
    phone = models.CharField(max_length=13, blank=True, null=True, verbose_name='Телефон')
    vk = models.CharField(max_length=50, blank=True, null=True, verbose_name='ВКонтакте')
    telegram = models.CharField(max_length=50, null=True, blank=True, verbose_name='Telegram')
    whatsapp = models.CharField(max_length=50, null=True, blank=True, verbose_name='WhatsApp')
    facebook = models.CharField(max_length=50, null=True, blank=True, verbose_name='Facebook')
    twitter = models.CharField(max_length=50, null=True, blank=True, verbose_name='Twitter')
    instagram = models.CharField(max_length=50, null=True, blank=True, verbose_name='Instagram')
    favourite = models.ManyToManyField(to='posts.Post', related_name='favourite_posts', blank=True,
                                       verbose_name='Избранные публикации')
    subscribed_categories = models.ManyToManyField(to='posts.Category', blank=True, related_name='category_subscribers',
                                                   verbose_name='Подписки на категории')
    subscribed_users = models.ManyToManyField(to='Profile', blank=True, related_name='user_subscriptions',
                                              verbose_name='Подписки на пользователей')
    objects = ProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        # return f'{self.user.username} Profile'
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    # получаем имя файла с изображением профиля
    def image_filename(self):
        return str(self.image)[str(self.image).index(f'photos/{self}/'):]

    # def save(self, *args, **kwargs):
    #     super(Profile, self).save(*args, **kwargs)
    #
    #     img = Image.open(self.image.path)
    #
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)
