# Pénzügyőr - Lokális Futtatási Útmutató 

<img width="2560" height="1032" alt="kép" src="https://github.com/user-attachments/assets/02489a35-4954-43d6-881a-227d8db406a0" />


## 1. Szükséges programok telepítése

Mielőtt elindítanád a projektet, két dologra lesz szükséged a gépeden:

* **Python:** A projekt futtatásához Python környezet szükséges (ajánlott: 3.10 vagy újabb). 
    * *Honnan szedd le?* Töltsd le a hivatalos oldalról: [python.org/downloads](https://www.python.org/downloads/)
    * *Fontos:* Telepítésnél (Windows alatt) pipáld be az **"Add Python to PATH"** lehetőséget!
* **Django keretrendszer:** Ha a Python már fent van, nyiss egy Parancssort (Terminal / CMD), és telepítsd a Djangót ezzel a paranccsal:
    ```bash
    pip install django
    ```

## 2. A projekt elindítása

Ha letöltötted a kódot a GitHubról, kövesd ezt a 3 lépést a terminálban:

1.  **Lépj be a projekt mappájába:** Navigálj abba a mappába, ahol a `manage.py` fájl található.
2.  **Adatbázis létrehozása:** Első indítás előtt létre kell hoznod a saját, lokális adatbázisodat. Ezt a parancsot csak egyszer kell lefuttatni:
    ```bash
    python manage.py migrate
    ```
3.  **Szerver indítása:** Röffentsd be a weboldalt a következő paranccsal:
    ```bash
    python manage.py runserver
    ```

Ezután nyisd meg a böngésződet, és írd be ezt a címet: **http://127.0.0.1:8000/**

## 3. Hogyan használd? (Mit teszteljetek?)

A rendszer úgy lett felépítve, hogy minden felhasználó csak a saját adatait látja. A teszteléshez kövessétek ezt az útvonalat:

1.  **Regisztráció / Belépés:** A főoldalon egyből a bejelentkező felület fogad (ha nem, kattints a kilépésre). Hozzatok létre egy új fiókot magatoknak a *Regisztráció* gombbal! A rendszer azonnal be is léptet.
2.  **Kategóriák létrehozása:** Mivel üres a fiókod, először kategóriákra lesz szükséged. Kattints az *Új tranzakció rögzítése* gombra, majd a lenyíló menü alatt válaszd az *+ Új kategória létrehozása* opciót. (Csinálj pl. egy "Fizetés" bevételt és egy "Élelmiszer" kiadást).
3.  **Pénzmozgás rögzítése:** Ha megvannak a kategóriák, vigyetek fel pár teszt tranzakciót (bevételeket és kiadásokat egyaránt).
4.  **Dashboard (Főoldal):** Térjetek vissza a főoldalra. Itt ellenőrizhetitek, hogy a rendszer helyesen számolja-e ki az egyenleget (Bevétel - Kiadás = Egyenleg), és jól listázza-e az utolsó tranzakciókat.
