"""
Seeder de desarrollo.

Uso:
    python manage.py seed                    # default: 5 users, 40 posts
    python manage.py seed --users 10 --posts 100
    python manage.py seed --flush             # borra antes de seedear

Crea:
- Superuser 'admin' / 'admin12345' (si no existe)
- N usuarios demo (user1, user2, ...) con password 'demo12345'
- M posts random distribuidos entre los usuarios
- Algunos likes y follows random
"""

import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Follow, User
from apps.posts.models import Like, Post


LOREM = [
    "Hola mundo desde Nandetuiter.",
    "Hoy aprendí algo nuevo sobre Django REST Framework.",
    "Angular 18 con signals está copado.",
    "¿Alguien probó django-constance? Cambia config sin redeploy.",
    "Pull request mergeado, día productivo.",
    "Tests pasan, hora de un café ☕",
    "Refactorizando el feed para que respete POSTS_PER_PAGE.",
    "Debuggeando un CORS error por la enésima vez...",
    "SQLite en dev es suficiente, Postgres queda para prod.",
    "Standalone components > NgModules.",
    "JWT access token expira en 15 min, refresh en 7 días.",
    "El admin de Django sigue siendo OP.",
    "Migraciones aplicadas sin drama.",
    "Frontend en :4200, backend en :8000, vida feliz.",
    "TIL: `select_related` evita N+1 queries.",
]


class Command(BaseCommand):
    help = 'Carga datos de prueba (users, posts, likes, follows).'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5)
        parser.add_argument('--posts', type=int, default=40)
        parser.add_argument('--flush', action='store_true',
                            help='Borra posts/likes/follows/users-demo antes de seedear')

    @transaction.atomic
    def handle(self, *args, **opts):
        n_users = opts['users']
        n_posts = opts['posts']

        if opts['flush']:
            self.stdout.write(self.style.WARNING('Flush: borrando datos demo...'))
            Like.objects.all().delete()
            Follow.objects.all().delete()
            Post.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        # 1. Superuser
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@nandetuiter.local',
                      'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('admin12345')
            admin.save()
            self.stdout.write(self.style.SUCCESS('+ superuser admin/admin12345'))
        else:
            self.stdout.write('= superuser admin ya existe')

        # 2. Usuarios demo
        users = [admin]
        for i in range(1, n_users + 1):
            u, c = User.objects.get_or_create(
                username=f'user{i}',
                defaults={'email': f'user{i}@nandetuiter.local'},
            )
            if c:
                u.set_password('demo12345')
                u.bio = f'Demo user #{i} — built by seeder.'
                u.save()
            users.append(u)
        self.stdout.write(self.style.SUCCESS(f'+ {n_users} users demo (password: demo12345)'))

        # 3. Posts
        existing = Post.objects.count()
        to_create = max(0, n_posts - existing)
        for _ in range(to_create):
            Post.objects.create(
                author=random.choice(users),
                content=random.choice(LOREM),
            )
        self.stdout.write(self.style.SUCCESS(
            f'+ {to_create} posts creados (total ahora: {Post.objects.count()})'
        ))

        # 4. Likes random
        posts = list(Post.objects.all())
        likes_created = 0
        for u in users:
            for p in random.sample(posts, k=min(len(posts), 8)):
                _, c = Like.objects.get_or_create(user=u, post=p)
                if c:
                    likes_created += 1
        self.stdout.write(self.style.SUCCESS(f'+ {likes_created} likes'))

        # 5. Follows random
        follows_created = 0
        for u in users:
            targets = [t for t in users if t != u]
            for t in random.sample(targets, k=min(len(targets), 3)):
                _, c = Follow.objects.get_or_create(follower=u, following=t)
                if c:
                    follows_created += 1
        self.stdout.write(self.style.SUCCESS(f'+ {follows_created} follows'))

        self.stdout.write(self.style.SUCCESS('\nSeed OK.'))
        self.stdout.write('Login admin: http://localhost:8000/admin/  (admin / admin12345)')
        self.stdout.write('Demo users:  user1..userN  (password: demo12345)')
