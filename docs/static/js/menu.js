function loadMenu() {
    fetch('/menu')
        .then(response => response.text())
        .then(data => {
            document.getElementById('menu-placeholder').innerHTML = data;
        })
        .catch(error => console.error('Ошибка загрузки меню:', error));
}

// Вызов функции загрузки меню при загрузке страницы
window.onload = loadMenu;
