from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Transaction, Category
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json


@login_required(login_url='/login/')
def dashboard(request):
    # 1. Kikeressük azokat a hónapokat, amikor volt tranzakciója a felhasználónak
    months_data = Transaction.objects.filter(user=request.user).annotate(
        month_trunc=TruncMonth('date')
    ).values('month_trunc').distinct().order_by('-month_trunc')

    # Szép magyar hónapnevek a legördülő listához
    hu_months = ['', 'Január', 'Február', 'Március', 'Április', 'Május', 'Június',
                 'Július', 'Augusztus', 'Szeptember', 'Október', 'November', 'December']

    available_months = []
    for m in months_data:
        dt = m['month_trunc']
        if dt:
            val = f"{dt.year}-{dt.month:02d}"
            disp = f"{dt.year}. {hu_months[dt.month]}"
            available_months.append({'value': val, 'display': disp})

    # 2. Hónap kiválasztása
    selected_month = request.GET.get('month')

    if not selected_month and available_months:
        selected_month = available_months[0]['value']
    elif not selected_month:
        now = timezone.now()
        selected_month = f"{now.year}-{now.month:02d}"

    year, month = map(int, selected_month.split('-'))

    # 3. Alapadatok lekérése a választott hónapra
    all_transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )

    # 4. Összesített statisztikák (kártyákhoz)
    income = all_transactions.filter(category__type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = all_transactions.filter(category__type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expense

    # 5. Kategóriánkénti csoportosítás (Diagramhoz)
    income_cats = all_transactions.filter(category__type='INCOME').values('category__name').annotate(
        total=Sum('amount')).order_by('-total')
    expense_cats = all_transactions.filter(category__type='EXPENSE').values('category__name').annotate(
        total=Sum('amount')).order_by('-total')

    # Előkészítjük az adatokat a Javascript számára
    cat_labels = [c['category__name'] for c in income_cats] + [c['category__name'] for c in expense_cats]

    # FIGYELEM! Itt a .total értékeket egész számmá (int) alakítjuk!
    cat_amounts = [int(c['total']) for c in income_cats] + [int(c['total']) for c in expense_cats]
    cat_colors = ['#198754'] * len(income_cats) + ['#dc3545'] * len(expense_cats)

    # ==========================================
    # 🕵️‍♂️ TARTÓTISZT (Pénzügyi Tanácsadó Motor)
    # ==========================================
    advisor_messages = []

    # 1. Előző KÉT hónap kiszámolása a "Nyereségszéria" vizsgálatához
    # Egy hónappal ezelőtt (pl. ha most március van, akkor február):
    prev1_month, prev1_year = (12, year - 1) if month == 1 else (month - 1, year)
    # Két hónappal ezelőtt (pl. ha most március van, akkor január):
    prev2_month, prev2_year = (12, prev1_year - 1) if prev1_month == 1 else (prev1_month - 1, prev1_year)

    # Első előző hónap (prev1) egyenlegének kiszámolása
    prev1_trans = Transaction.objects.filter(user=request.user, date__year=prev1_year, date__month=prev1_month)
    prev1_inc = prev1_trans.filter(category__type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    prev1_exp = prev1_trans.filter(category__type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    prev1_balance = prev1_inc - prev1_exp

    # Második előző hónap (prev2) egyenlegének kiszámolása
    prev2_trans = Transaction.objects.filter(user=request.user, date__year=prev2_year, date__month=prev2_month)
    prev2_inc = prev2_trans.filter(category__type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    prev2_exp = prev2_trans.filter(category__type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    prev2_balance = prev2_inc - prev2_exp

    # Szabály 1: Nyereségszéria (Az előző 2 LEZÁRT hónap pluszban volt)
    if prev1_balance > 0 and prev2_balance > 0:
        advisor_messages.append({
            'type': 'success',
            'icon': '📈',
            'text': 'Kiváló munka! Az előző két lezárt hónapot stabil nyereséggel zártad. Érdemes elgondolkodnod a felhalmozott többlet lekötésén (pl. állampapír vagy vésztartalék)!'
        })
    # Szabály 2: Deficit Riasztó (Több a kiadás, mint a bevétel)
    if balance < 0:
        advisor_messages.append({
            'type': 'danger',
            'icon': '🚨',
            'text': 'Figyelem! Jelenleg masszív deficitben vagy, a kiadásaid meghaladják a bevételeidet. Húzd be a kéziféket a hónap hátralévő részében!'
        })

    # Szabály 3: Kategória-figyelő (Több mint 20% elmegy egy dologra)
    if income > 0:
        for cat in expense_cats:
            if int(cat['total']) > (int(income) * 0.20):
                advisor_messages.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'text': f"A bevételeid több mint 20%-át elviszi a(z) '{cat['category__name']}' kategória! Ha spórolni akarsz, itt érdemes megfognod a pénzt."
                })

    # Szabály 4: Inaktivitás figyelő (Ha 10 napja nem volt mozgás) - KIHÚZVA A SZÉLÉRE!
    now_date = timezone.now().date()

    # Megkeressük a legutolsó rögzített tranzakciót (bármikori is legyen az)
    last_transaction = Transaction.objects.filter(user=request.user).order_by('-date').first()

    if last_transaction:
        # Kiszámoljuk a különbséget (mai nap mínusz az utolsó tranzakció napja)
        days_since_last = (now_date - last_transaction.date).days

        if days_since_last > 10:
            # Szép formátummá alakítjuk a dátumot (pl. 2026. 04. 01.)
            last_date_str = last_transaction.date.strftime("%Y. %m. %d.")
            advisor_messages.append({
                'type': 'info',
                'icon': '🗓️',
                'text': f'Figyelem! Már {days_since_last} napja nem rögzítettél új tételt (utolsó: {last_date_str}). Ne hagyd felgyülemleni a blokkokat a pénztárcádban!'
            })
    else:
        # Ha még az égvilágon semmit nem rögzített a fiókjában
        if now_date.day > 10:
            advisor_messages.append({
                'type': 'info',
                'icon': '🗓️',
                'text': f'Már a hónap {now_date.day}. napja van, de még sosem rögzítettél tranzakciót. Kezdd el a naplózást a pontos statisztikákhoz!'
            })

    # Ha minden tökéletes, és egyik szabály sem riasztott:
    if not advisor_messages and all_transactions.exists():
        advisor_messages.append({
            'type': 'secondary',
            'icon': '🛡️',
            'text': 'A pénzügyi mutatóid jelenleg stabilak, nem találtam kirívó anomáliát a rendszerben. Csak így tovább!'
        })

    # Ha minden tökéletes, és egyik szabály sem riasztott:
    if not advisor_messages and all_transactions.exists():
        advisor_messages.append({
            'type': 'secondary',
            'icon': '🛡️',
            'text': 'A pénzügyi mutatóid jelenleg stabilak, nem találtam kirívó anomáliát a rendszerben. Csak így tovább!'
        })

    # Ha minden tökéletes, és egyik szabály sem riasztott:
    if not advisor_messages and all_transactions.exists():
        advisor_messages.append({
            'type': 'secondary',
            'icon': '🛡️',
            'text': 'A pénzügyi mutatóid jelenleg stabilak, nem találtam kirívó anomáliát a rendszerben. Csak így tovább!'
        })

    context = {
        'transactions': all_transactions.order_by('-date'),
        'total_income': income,
        'total_expense': expense,
        'balance': balance,
        'selected_month': selected_month,
        'available_months': available_months,

        # FIGYELEM! A json.dumps() biztosítja a hibátlan Javascript adatátadást
        'cat_labels': json.dumps(cat_labels),
        'cat_amounts': json.dumps(cat_amounts),
        'cat_colors': json.dumps(cat_colors),
        'advisor_messages': advisor_messages,
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