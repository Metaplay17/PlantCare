const passwordRegex = /^(?=.*\d)(?=.*[A-Z]).{8,30}$/;
let email;

document.getElementById("send-code-btn").addEventListener("click", async (event) => {
    event.preventDefault();
    email = document.getElementById("email").value;
    let response = await fetch("https://localhost/auth/send-recover-code", {
        method: 'POST',
        body: JSON.stringify({"email": email}),
        headers: {
        'Content-Type': 'application/json; charset=UTF-8'
        }
    });
    if (response.status == 200) {
        document.getElementById("step-code").style.display = "flex";
    }
    else if (response.status == 404) {
        alert("Пользователя с таким email не существует");
        return;
    }
    else if (response.status == 425) {
        alert("Попробуйте еще раз через несколько минут");
        return;
    }
    else {
        alert("Internal Server Error");
        return;
    }
});

document.getElementById("reset-password-btn").addEventListener("click", async (event) => {
    event.preventDefault();
    let code = document.getElementById("code").value;
    let newPassword = document.getElementById("new-password").value;
    let confirmPassword = document.getElementById("confirm-password").value;

    if (!passwordRegex.test(newPassword)) {
        alert("Длина пароля от 8 до 30 символов, обязательно наличие цифры и заглавной буквы");
        return;
    }
    else if (newPassword != confirmPassword) {
        alert("Пароли не совпадают");
        return;
    }

    let resp = await fetch("https://localhost/auth/recover-password", {
        method: 'POST',
        body: JSON.stringify({
            "email": email,
            "new_password": newPassword,
            "code": code
        }),
        headers: {
        'Content-Type': 'application/json; charset=UTF-8'
        }
    });
    if (resp.status == 400) {
        alert("Проверьте заполнение полей");
        return;
    }
    else if (resp.status == 403) {
        alert("Неверный код");
        return;
    }
    else if (resp.status == 404) {
        alert("Пользователь с таким email не найден");
        return;
    }
    else if (resp.status == 425) {
        alert("Попробуйте еще раз через несколько минут");
        return;
    }
    else if (resp.status != 200) {
        alert("Internal Server Error")
        return;
    }
    else {
        window.location.href = "/login";
    }
});

