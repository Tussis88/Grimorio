window.onload = function() {
    // var toggleHide = document.getElementById("toggleHide");
    
    // salva la scroll position ogni volta che la pagina viene scrollata
    function handleScroll() {
        var scrollPosition = window.scrollY;
        localStorage.setItem("scrollPosition", scrollPosition);
    }
    window.addEventListener("scroll", handleScroll);

    // toggleHide.addEventListener("change", function() {
    //     var hiddenElements = document.querySelectorAll(".hidden");
    //
    //     for (var i = 0; i < hiddenElements.length; i++) {
    //         if (!toggleHide.checked) {
    //             hiddenElements[i].style.display = "none";
    //         } else {
    //             hiddenElements[i].style.display = "table-cell";
    //         }
    //     }
        // salva lo stato nel localStorage
        // localStorage.setItem("toggleHideState", toggleHide.checked);
    // });

    // carica lo stato del checkbox dallo storage
    var savedState = localStorage.getItem("toggleHideState");
    if (savedState) {
        toggleHide.checked = JSON.parse(savedState);
        // triggera lo stato iniziale dell'evento
        toggleHide.dispatchEvent(new Event("change"));
    }
    var savedScrollPosition = localStorage.getItem("scrollPosition");
    if (savedScrollPosition) {
        window.scrollTo(0, savedScrollPosition);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    // prende tutti gli elementi "navbar-burger"
    const $navbarBurgers = Array.prototype.slice.call(
        document.querySelectorAll(".navbar-burger"),
        0,
    );

    // aggiunge un click event ad ogni navbar
    $navbarBurgers.forEach((el) => {
        el.addEventListener("click", () => {
            // recupera il data-target da ogni navbar
            const target = el.dataset.target;
            const $target = document.getElementById(target);

            // attiva/disattiva la funzione "is-active" per ogni elemento
            el.classList.toggle("is-active");
            $target.classList.toggle("is-active");
        });
    });
});
