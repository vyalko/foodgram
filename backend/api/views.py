from io import BytesIO

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, CustomUserSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeSerializer, RecipeWriteSerializer,
                             ShortLinkSerializer, SubscriptionSerializer,
                             TagSerializer)
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, ShortLink, Tag)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser, Subscription

User = get_user_model()


def redirect_short_link(request, short_url):
    try:
        short_link = ShortLink.objects.get(short_url=short_url)
        return redirect(short_link.original_url)
    except ShortLink.DoesNotExist:
        raise Http404("Short link does not exist.")


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user
        data = request.data

        if request.method == 'PUT' and 'avatar' not in data:
            return Response(
                {'detail': 'Поле "avatar" отсутствует.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPagination
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribers__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(CustomUser, id=author_id)

        if user == author:
            return Response(
                {'errors': 'Невозможно подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)

            serializer = SubscriptionSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user, author=author
            ).first()
            if subscription:
                subscription.delete()
                return Response({'detail': 'Подписка отменена.'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Подписка не найдена.'},
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response({'detail': 'Страница не найдена.'},
                            status=status.HTTP_404_NOT_FOUND)
        recipe = self.get_object()

        user = request.user

        if request.method == 'POST':
            if user.favorites.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)

            serializer = RecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = user.favorites.filter(recipe=recipe)
            if not favorite.exists():
                return Response({'errors': 'Рецепта нет в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            favorite.delete()
            return Response({'status': 'Рецепт удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)

            ShoppingCart.objects.create(user=user, recipe=recipe)

            serializer = RecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_cart = user.shopping_cart.filter(recipe=recipe)
            if not shopping_cart.exists():
                return Response({'errors': 'Рецепта нет в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)

            shopping_cart.delete()
            return Response({'status': 'Рецепт удалён из корзины'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""

        recipe = get_object_or_404(Recipe, pk=pk)
        original_url = request.build_absolute_uri(
            reverse('api:recipe-detail', kwargs={'pk': recipe.pk}))

        short_link, created = ShortLink.objects.get_or_create(
            original_url=original_url)

        serializer = ShortLinkSerializer(short_link)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)

        if not shopping_cart.exists():
            return Response({'error': 'Корзина пуста'},
                            status=status.HTTP_400_BAD_REQUEST)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        pdfmetrics.registerFont(
            TTFont('ArialMT', '/usr/share/fonts/truetype/arialmt.ttf')
        )
        p.setFont('ArialMT', 12)

        p.drawString(100, 750, "Список покупок:")

        start_height = 700
        for item in shopping_cart:
            ingredients = RecipeIngredient.objects.filter(recipe=item.recipe)
            for ingredient in ingredients:
                p.drawString(
                    100,
                    start_height,
                    f"{ingredient.ingredient.name} - {ingredient.amount}/"
                    f"{ingredient.ingredient.measurement_unit}")
                start_height -= 20

        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_cart.pdf')
