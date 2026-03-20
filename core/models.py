from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Kategóriák táblája (pl. Élelmiszer, Rezsi, Fizetés)"""

    TRANSACTION_TYPES = [
        ('INCOME', 'Bevétel'),
        ('EXPENSE', 'Kiadás'),
    ]

    name = models.CharField(max_length=100, verbose_name="Kategória neve")
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Típus")

    # A felhasználóhoz kötjük a kategóriáit, hogy mindenki csak a sajátját lássa:
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    """Tranzakciók táblája (A bevételek és kiadások rögzítése)"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Kategória")
    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Összeg (Ft)")
    date = models.DateField(default=timezone.now, verbose_name="Dátum")
    description = models.CharField(max_length=255, blank=True, verbose_name="Megjegyzés")

    def __str__(self):
        return f"{self.date} - {self.category.name}: {self.amount} Ft"

    @property
    def is_expense(self):
        return self.category.type == 'EXPENSE'