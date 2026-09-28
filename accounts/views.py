import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile

# 1. REGISTER VIEW
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is already taken!")
            return redirect('register')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)

        messages.success(request, "Account created successfully! Please sign in.")
        return redirect('login')

    return render(request, 'client/register.html')


# 2. LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user_obj = User.objects.filter(email__iexact=username_or_email).first() or \
                   User.objects.filter(username__iexact=username_or_email).first()

        username = user_obj.username if user_obj else username_or_email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('profile')
        else:
            messages.error(request, "Invalid credentials! Please try again.")
            return redirect('login')

    return render(request, 'client/login.html')


# 3. LOGOUT VIEW
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')


# 4. FORGOT PASSWORD VIEW
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email__iexact=email).first()

        if user:
            otp = str(random.randint(1000, 9999))
            request.session['reset_user_id'] = user.id
            request.session['reset_otp'] = otp

            subject = "Password Reset Verification Code"
            message = f"Your 4-digit OTP to reset password is: {otp}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, "OTP sent to your email address!")
            return redirect('reset_password')
        else:
            messages.error(request, "No account found with this email!")
            return redirect('forgot_password')

    return render(request, 'client/forgot_password.html')


# 5. RESET PASSWORD VIEW
def reset_password_view(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        session_otp = request.session.get('reset_otp')
        reset_user_id = request.session.get('reset_user_id')

        if not session_otp or not reset_user_id:
            messages.error(request, "Session expired! Please request OTP again.")
            return redirect('forgot_password')

        if user_otp != session_otp:
            messages.error(request, "Invalid OTP code!")
            return redirect('reset_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('reset_password')

        try:
            user = User.objects.get(id=reset_user_id)
            user.set_password(new_password)
            user.save()

            del request.session['reset_otp']
            del request.session['reset_user_id']

            messages.success(request, "Password reset successfully! Please login.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User account not found!")
            return redirect('forgot_password')

    return render(request, 'client/reset_password.html')


# 6. PROFILE VIEW
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'client/profile.html', {'profile': profile})


# 7. CHANGE PASSWORD VIEW
@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "Your current password is incorrect.")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('change_password')

        request.user.set_password(new_password)
        request.user.save()

        login(request, request.user)
        messages.success(request, "Your password was updated successfully!")
        return redirect('profile')

    return render(request, 'client/change_password.html')


# 8. EDIT PROFILE VIEW
@login_required
def edit_profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.save()

        profile.phone = request.POST.get('phone', '').strip()
        profile.pincode = request.POST.get('pincode', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.city = request.POST.get('city', '').strip()
        profile.state = request.POST.get('state', '').strip()
        profile.country = request.POST.get('country', '').strip()

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'client/edit_profile.html', {
        'profile': profile,
        'user': request.user
    })