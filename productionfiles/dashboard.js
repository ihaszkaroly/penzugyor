const show_more_button = document.querySelector("#show-more-btn");
const month_buttons = document.querySelector("#month-list");

show_more_button.addEventListener("click", loadMoreTransactions);
month_buttons.addEventListener("click", sortByMonth);

function loadMoreTransactions(event) {
    const extra_items = document.querySelectorAll(".extra-item");
    extra_items.forEach(item => {
        item.classList.remove("d-none");
        item.classList.remove("extra-item");
    });

    show_more_button.classList.add("d-none");
}

function sortByMonth(event) {
    const btn = event.target;
    if (!btn.classList.contains("month-btn")) return;

    const selectedMonthText = btn.textContent.trim();
    const items = document.querySelectorAll("#transaction-list li");

    let income = 0;
    let expense = 0;

    // Aktív gomb megnyomásával visszakapjuk az eredeti listát.
    if (btn.classList.contains("active")) {
        btn.classList.remove("active");
        
        let today = new Date().toLocaleDateString('hu-HU', { year: 'numeric', month: 'long' });

        let i = 1;
        items.forEach(item => {
            if (i <= 10) item.classList.remove("d-none");
            else {
                item.classList.add("d-none");
                item.classList.add("extra-item");
            }

            const dateTextFull = item.querySelector("div").textContent.trim().split("|")[0];
            const dateTextYear = dateTextFull.split(" ")[0];
            const dateTextMonth = dateTextFull.split(" ")[1];
            const dateText = dateTextYear.concat(" ", dateTextMonth);

            const value = item.querySelector("span").textContent.trim().slice(1).split(" ")[0];

            if (today == dateText) {
                if (item.querySelector("span").classList.contains("bg-success"))
                    income += parseInt(value);
                if (item.querySelector("span").classList.contains("bg-danger"))
                    expense += parseInt(value);
            }

            i++;
        });

        document.querySelector("#month-info").innerHTML = "Tranzakciós összefoglaló " + today + ":";
        document.querySelector("#card-income").innerHTML = income + " Ft";
        document.querySelector("#card-expense").innerHTML = expense + " Ft";

        if (items.length > 10) show_more_button.classList.remove("d-none");
        else show_more_button.classList.add("d-none");

        return;
    }

    // Csak a kattintott gomb lesz aktív:
    document.querySelectorAll(".month-btn").forEach(btn => { btn.classList.remove("active"); });
    btn.classList.add("active");

    loadMoreTransactions();

    // Lista szűrése:
    let j = 1;
    items.forEach(item => {
        const dateTextFull = item.querySelector("div").textContent.trim().split("|")[0];
        const dateTextYear = dateTextFull.split(" ")[0];
        const dateTextMonth = dateTextFull.split(" ")[1];
        const dateText = dateTextYear.concat(" ", dateTextMonth);

        if (dateText == selectedMonthText) {
            item.classList.remove("d-none");

            if (j > 10) {
                item.classList.add("d-none");
                item.classList.add("extra-item");
            }

            const value = item.querySelector("span").textContent.trim().slice(1).split(" ")[0];

            if (item.querySelector("span").classList.contains("bg-success"))
                income += parseInt(value);
            if (item.querySelector("span").classList.contains("bg-danger"))
                expense += parseInt(value);

            j++;
        }
        else item.classList.add("d-none");
    });

    // Összefoglaló kártyák frissítése adott hónapra:
    document.querySelector("#month-info").innerHTML = "Tranzakciós összefoglaló " + selectedMonthText + ":";
    document.querySelector("#card-income").innerHTML = income + " Ft";
    document.querySelector("#card-expense").innerHTML = expense + " Ft";

    if (j > 10) show_more_button.classList.remove("d-none");
}