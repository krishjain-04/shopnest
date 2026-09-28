/* ===================================================================
   ShopNest Admin Console - Dedicated Login JavaScript
   File: static/adminjs/adminloginjs.js
   =================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    const togglePasswordBtn = document.getElementById('togglePasswordBtn');
    const passwordInput = document.getElementById('adminPasswordInput');
    const usernameInput = document.getElementById('adminUsernameInput');

    // 1. Password Visibility Toggle
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            const icon = togglePasswordBtn.querySelector('i');
            if (icon) {
                if (isPassword) {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                    togglePasswordBtn.setAttribute('title', 'Hide password');
                    togglePasswordBtn.setAttribute('aria-label', 'Hide password');
                } else {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                    togglePasswordBtn.setAttribute('title', 'Show password');
                    togglePasswordBtn.setAttribute('aria-label', 'Show password');
                }
            }
        });
    }

    // 2. Autofocus on username input if empty, otherwise password
    if (usernameInput) {
        if (!usernameInput.value) {
            usernameInput.focus();
        } else if (passwordInput) {
            passwordInput.focus();
        }
    }
});
