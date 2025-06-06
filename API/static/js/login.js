const passwordRegex = /^(?=.*\d)(?=.*[A-Z]).{8,30}$/;
const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;

document.getElementById("login-btn").addEventListener("click", async (event) => {
    event.preventDefault();

    let login = document.getElementById("login").value;
    let password = document.getElementById("password").value;
    if (!passwordRegex.test(password)) {
        alert("Пароль длиной от 8 до 30 символов без специальных символов");
        return;
    }
    if (!usernameRegex.test(login)) {
        alert("Логин длиной от 3 до 20 символов без специальных символов");
        return;
    }

    data = {
        "login": login,
        "password": password
    };
    let response = await fetch('/auth/login', {
        method: "POST",
        body: JSON.stringify(data),
        credentials: "include",
        headers: {
        'Content-Type': 'application/json; charset=UTF-8'
        }
    });
    let message = await response.json();
    if (response.status != 200) {
        alert(message["status"])
        return;
    }
    else {
        window.location.href = '/';
    }

})