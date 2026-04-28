from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    userID = models.IntegerField(primary_key=True)
    first = models.CharField(max_length=255)
    last = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mailing_address = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return f"{self.first} {self.last}"


class Author(models.Model):
    """Author model"""
    authorID = models.IntegerField(primary_key=True)
    first = models.CharField(max_length=255)
    last = models.CharField(max_length=255)
    bio = models.TextField(max_length=4111, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'Authors'

    def __str__(self):
        return f"{self.first} {self.last}"


class Book(models.Model):
    """Book model"""
    bookID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    series_name = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column='authorID')
    publisher = models.CharField(max_length=255, blank=True)
    pub_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    in_circulation_from = models.DateField(null=True, blank=True)
    in_circulation_until = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'Books'

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        """Check if book is currently available for checkout"""
        from django.utils import timezone
        now = timezone.now().date()
        if self.in_circulation_from and self.in_circulation_until:
            return self.in_circulation_from <= now <= self.in_circulation_until
        elif self.in_circulation_from:
            return self.in_circulation_from <= now
        return True


class Checkout(models.Model):
    """Checkout model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='bookID')
    out_time = models.DateTimeField()
    in_time = models.DateTimeField(null=True, blank=True)
    due_time = models.DateTimeField()
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'Checkouts'
        unique_together = [['user', 'book', 'out_time']]

    def __str__(self):
        return f"{self.user} checked out {self.book}"

    @property
    def is_overdue(self):
        """Check if checkout is overdue"""
        from django.utils import timezone
        return self.due_time < timezone.now() and self.in_time is None


class Reservation(models.Model):
    """Reservation model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='bookID')
    reservation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Reservations'
        unique_together = [['user', 'book']]

    def __str__(self):
        return f"{self.user} reserved {self.book}"


class Review(models.Model):
    """Review model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
    book_name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='bookID')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column='authorID')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        db_table = 'Reviews'
        unique_together = [['user', 'book', 'author']]

    def __str__(self):
        return f"{self.user} rated {self.book} - {self.score}/10"


class FavoriteAuthor(models.Model):
    """Favorite authors model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column='authorID')

    class Meta:
        db_table = 'FavoriteAuthors'
        unique_together = [['user', 'author']]

    def __str__(self):
        return f"{self.user} favorites {self.author}"


class FavoriteBook(models.Model):
    """Favorite books model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='bookID')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column='authorID')  # Redundant but in schema

    class Meta:
        db_table = 'FavoriteBooks'
        unique_together = [['user', 'book', 'author']]

    def __str__(self):
        return f"{self.user} favorites {self.book}"


class Promotion(models.Model):
    """Promotion model"""
    promID = models.IntegerField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='bookID')
    discount_percent = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = 'Promotions'
        unique_together = [['promID', 'book']]

    def __str__(self):
        return f"{self.discount_percent}% off {self.book}"

    @property
    def is_active(self):
        """Check if promotion is currently active"""
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def get_discounted_price(self):
        """Calculate discounted price"""
        if self.is_active:
            discount_amount = self.book.price * (self.discount_percent / 100)
            return self.book.price - discount_amount
        return self.book.price
