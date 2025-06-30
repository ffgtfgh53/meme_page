const user = document.getElementById('user')
const pass = document.getElementById('pass')
const userRegExp = /^\w+$/

user.addEventListener("input", (event) => {
    if (user.validity.valueMissing) {
        user.setCustomValidity('Username is required')
    } else if (user.validity.tooShort) {
        user.setCustomValidity('Username must be at least 4 characters')
    } else if (!userRegExp.test(user.value)) {
        user.setCustomValidity('Username must only contain letters and numbers')
    } else {
        user.setCustomValidity("")
    }
})

pass.addEventListener("input", (event) => {
    if (pass.validity.tooShort) {
        pass.setCustomValidity('Password must be at least 8 characters')
    } else {
        pass.setCustomValidity("")
    }
})