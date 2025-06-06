const passwordRegex = /^(?=.*\d)(?=.*[A-Z]).{8,30}$/;
const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;

document.getElementById("register-btn").addEventListener("click", async (event) => {
    event.preventDefault();
    let login = document.getElementById("login").value;
    let email = document.getElementById("email").value;
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirm-password").value;

    if (!usernameRegex.test(login)) {
        alert("Длина логина от 3 до 20 символов, без специальных символов");
        return;
    }

    if (!usernameRegex.test(username)) {
        alert("Длина имени пользователя от 3 до 20 символов, без специальных символов");
        return;
    }

    if (!passwordRegex.test(password)) {
        alert("Длина пароля от 8 до 30 символов, обязательно наличие цифры и заглавной буквы");
        return;
    }

    if (password !== confirmPassword) {
        alert("Пароли не совпадают");
        return;
    }
    let data = {
        "login": login,
        "email": email,
        "username": username,
        "password": password,
        "confirm_password": confirmPassword
    };
    let response = await fetch("/register", {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
        'Content-Type': 'application/json; charset=UTF-8'
        }
    });

    let ans = await response.json();
    if (response.status != 200) {
        alert(ans["status"]);
    }
    else {
        window.location.href = "http://localhost/login";
    }
    
});