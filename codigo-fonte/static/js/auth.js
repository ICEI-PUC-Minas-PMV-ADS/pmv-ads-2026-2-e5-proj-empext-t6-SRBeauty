const form = document.querySelector('#loginForm');
const email = document.querySelector('#email');
const password = document.querySelector('#password');
const toggle = document.querySelector('#togglePassword');
const emailError = document.querySelector('#emailError');
const passwordError = document.querySelector('#passwordError');

if (toggle && password) {
  toggle.addEventListener('click', () => {
    const hidden = password.type === 'password';
    password.type = hidden ? 'text' : 'password';
    toggle.setAttribute('aria-label', hidden ? 'Ocultar senha' : 'Mostrar senha');
  });
}

if (form) {
  form.addEventListener('submit', (event) => {
    emailError.textContent = '';
    passwordError.textContent = '';
    let valid = true;

    if (!email.value.trim() || !email.validity.valid) {
      emailError.textContent = 'Digite um e-mail válido.';
      valid = false;
    }
    if (!password.value.trim()) {
      passwordError.textContent = 'Digite sua senha.';
      valid = false;
    }
    if (!valid) event.preventDefault();
  });
}
