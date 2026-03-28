from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Transaction, Category
from django.shortcuts import render, redirect, get_object_or_404


@login_required(login_url='/login/')
def dashboard(request):
    """A főoldal logikája"""
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    total_income = user_transactions.filter(category__type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = user_transactions.filter(category__type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    context = {
        'transactions': user_transactions[:10],
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='/login/')
def add_transaction(request):
    """Új tranzakció hozzáadása"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category_id = request.POST.get('category_id')
        date = request.POST.get('date')
        description = request.POST.get('description')

        try:
            category = Category.objects.get(id=category_id, user=request.user)
            Transaction.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                date=date,
                description=description
            )
            return redirect('dashboard')
        except Category.DoesNotExist:
            pass

    user_categories = Category.objects.filter(user=request.user)
    return render(request, 'add_transaction.html', {'categories': user_categories})


# --- ÚJ FIÓKKEZELŐ FÜGGVÉNYEK ---

def register_user(request):
    """Regisztrációs oldal logikája"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    """Bejelentkezés logikája"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_user(request):
    """Kijelentkezés logikája"""
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def add_category(request):
    """Új kategória létrehozása a bejelentkezett felhasználónak"""
    if request.method == 'POST':
        name = request.POST.get('name')
        cat_type = request.POST.get('type')

        # Létrehozzuk és lementjük a kategóriát, szigorúan a request.user-hez kötve!
        Category.objects.create(
            name=name,
            type=cat_type,
            user=request.user
        )
        # Ha kész, visszadobjuk a tranzakció rögzítő oldalra, hogy egyből használhassa is
        return redirect('add_transaction')

    return render(request, 'add_category.html')

@login_required(login_url='/login/')
def delete_transaction(request, transaction_id):
    """Tranzakció törlése (Szigorúan ellenőrizve, hogy az övé-e)"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction.delete()
    return redirect('dashboard')

def privacy_policy(request):
    """Adatkezelési tájékoztató megjelenítése"""
    return render(request, 'privacy.html')