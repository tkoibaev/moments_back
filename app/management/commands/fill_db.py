from django.core.management.base import BaseCommand, CommandError
from app.models import CustomUser, Subscription, Moment, Comment, Tag, Like
from faker import Faker
import random

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()

        # Создание пользователей
        for _ in range(ratio):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            bio = fake.text(max_nb_chars=200) 
            avatar = fake.image_url(width=155, height=155) 

            CustomUser.objects.create_user(username=username, email=email, password=password, bio=bio, avatar=avatar)
        
        # Создание тегов
        for _ in range(ratio): # Создание 100 тегов
            tag_name = fake.word()
            tag = Tag.objects.create(name=tag_name)   

        # Создание моментов с случайным тегом
        for _ in range(ratio * 100):
            author = CustomUser.objects.order_by('?').first()
            description = fake.text(max_nb_chars=500) 
            image = fake.image_url(width=155, height=155) 
            tag = Tag.objects.order_by('?').first()
            moment = Moment.objects.create(author=author, description=description, image=image)
            moment.tag.add(tag) 

        # Создание комментов
        for _ in range(ratio * 1000):
            author = CustomUser.objects.order_by('?').first()
            moment = Moment.objects.order_by('?').first()
            content = fake.text(max_nb_chars=100) 
            Comment.objects.create(author=author, moment=moment, content=content)

        # Создание подписок
        for _ in range(ratio * 100):
            author = CustomUser.objects.order_by('?').first()
            subscriber = CustomUser.objects.order_by('?').first()
            
            while author == subscriber:
                subscriber = CustomUser.objects.order_by('?').first()

            Subscription.objects.create(author=author, subscriber=subscriber)
    
        # Создание лайков для моментов и комментов
        for _ in range(ratio * 1000):
            author = CustomUser.objects.order_by('?').first()
            like_object = random.choice([Moment.objects.order_by('?').first(), Comment.objects.order_by('?').first()])
            if isinstance(like_object, Moment):
                Like.objects.create(author=author, moment=like_object)
                self.stdout.write(self.style.SUCCESS(f'Добавлен лайк к моменту: {like_object.description[:50]}...'))
            elif isinstance(like_object, Comment):
                Like.objects.create(author=author, comment=like_object)
                self.stdout.write(self.style.SUCCESS(f'Добавлен лайк к комментарию: {like_object.content[:50]}...'))

        self.stdout.write(self.style.SUCCESS(f'Заполнили)'))
