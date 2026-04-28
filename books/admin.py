from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    User,
    Author,
    Book,
    Checkout,
    Reservation,
    Review,
    FavoriteAuthor,
    FavoriteBook,
    Promotion,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('userID', 'username', 'first', 'last', 'email', 'is_active', 'is_staff')
    search_fields = ('username', 'first', 'last', 'email')
    ordering = ('userID',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first', 'last', 'email', 'mailing_address', 'zipcode', 'balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('authorID', 'first', 'last', 'city', 'country')
    search_fields = ('first', 'last', 'city', 'country')
    ordering = ('last', 'first')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('bookID', 'name', 'author', 'publisher', 'genre', 'price', 'is_available')
    search_fields = ('name', 'series_name', 'author__first', 'author__last', 'genre', 'publisher')
    list_filter = ('genre', 'publisher')
    ordering = ('name',)
    readonly_fields = ('is_available',)


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'out_time', 'due_time', 'in_time', 'fine', 'is_overdue')
    search_fields = ('user__username', 'user__first', 'user__last', 'book__name')
    list_filter = ('out_time', 'due_time', 'in_time')
    ordering = ('-out_time',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'reservation_time')
    search_fields = ('user__username', 'user__first', 'user__last', 'book__name')
    list_filter = ('reservation_time',)
    ordering = ('-reservation_time',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'score')
    search_fields = ('user__username', 'book__name', 'book_name')
    list_filter = ('score',)
    ordering = ('-score',)


@admin.register(FavoriteAuthor)
class FavoriteAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__first', 'author__last')
    ordering = ('user',)


@admin.register(FavoriteBook)
class FavoriteBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'author')
    search_fields = ('user__username', 'book__name', 'author__first', 'author__last')
    ordering = ('user',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('promID', 'book', 'discount_percent', 'start_time', 'end_time', 'is_active')
    search_fields = ('book__name',)
    list_filter = ('discount_percent', 'start_time', 'end_time')
    ordering = ('-start_time',)
    readonly_fields = ('is_active',)
