from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q

from base64 import urlsafe_b64encode, urlsafe_b64decode
from django.utils.encoding import force_bytes, force_text

from django.template.loader import render_to_string
from .models import UserResetPassword
from pizza.settings import EMAIL_SENDER

import json
# Create your views here.

def new_user(request):
    '''
    This function check the data singin is valid, the username and e-mail 
    are available.
    If the new user is valid, create it and login.
    Return False if the data are not valid, otherwise return True.
    '''
    print('New User Request')
    username = request.POST['username']
    password = request.POST['password']
    pass_check = request.POST['pass-check']
    e_mail = request.POST['e-mail']
    first_name = request.POST['first-name']
    last_name = request.POST['last-name']

    if not (password == pass_check):
        context = {
            'success': False, 
            'message': ['Confirm Password must be equal than Password.'],
            'error': 'password'
            }
        return False, context


    user = User(username=username, password=password, email=e_mail,
                first_name=first_name,last_name=last_name)
    try:
        validate_password(user.password, user)
    except ValidationError as e:
        
        context = {
            'success': False, 
            'message': list(e),
            'error': 'password'
            }
        return False, context
    
    if not User.objects.filter(Q(username=username)|Q(email=e_mail)):
        user.save()
        login(request, user)
        context = {
            'success': True,
            'message': None
            }
        return True, context
    
    context = {
        'success': False,
        'message': ['The username or e-mail already exists.'],
        'error': 'username'
        }
    return False, context

def signin_view(request):
    '''
    Render the Singin Page if the user is not already login.
    '''
    print('Registration')
    if not request.user.is_authenticated:
        if request.method == 'POST':
            response, context = new_user(request)
            if response:
                context['redirect'] = reverse("orders:profile")
            return JsonResponse(context)

        return render(request, "registration/signin.html")
    
    return HttpResponseRedirect(reverse("orders:profile"))

def login_view(request):
    '''
    Login a user request. If the credentials are not valid return to Login Page.
    '''
    print('Login')
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            response = {
                'success': True,
                'redirect': reverse("orders:profile")
            }
        else:
            response = {
                'success': False,
                'error': 'credentials',
                'message': 'Invalid credentials'
            }
        return JsonResponse(response)
    
    return render(request, "registration/login.html")

def logout_view(request):
    '''
    Logout the user and redirect to Index Page.
    '''
    print('Logout')
    logout(request)
    return HttpResponseRedirect(reverse("orders:index"))

def direct_login(request):
    '''
    Same as login_view but from login from in Index Page.
    If credentials are invalid Login Page.
    '''
    if request.method == 'POST':
        response = login_view(request)
        data = json.loads(response.content)
        if data['success']:
            return HttpResponseRedirect(data['redirect'])
    return render(request, "registration/login.html")

def owner_login_view(request):
    '''
    Login for owners. If the user has not Staff Permission redirect to
    Profile Page, otherwise redirect to Orders Manage Page.
    '''
    print('Owner Login')
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            login(request, user)
            response = {'success': True}
            if user.is_staff:
                response['redirect'] = reverse("orders:owner_orders")
            else:
                response['redirect'] = reverse("orders:profile")
        else:
            response = {
                'success': False,
                'error': 'credentials',
                'message': 'Invalid credentials'
            }
        return JsonResponse(response)
    
    return render(request, "registration/owner_login.html", {"message": None})

def password_reset(request):
    '''
    Handle the reset password request.
    Send an email with a link for reset password.
    If the user email not match any user, do nothing.
    '''
    print('Password Reset')
    if request.method == 'POST':
        email = request.POST['email']
    
        try:
            
            user = User.objects.get(email=email)
            user.set_unusable_password()
            user.save()
            
            try:
                # Search if user already has a token
                reset = UserResetPassword.objects.get(user=user)
            except UserResetPassword.DoesNotExist:
                # Create the user token
                reset = UserResetPassword(user=user)
            
            # Save to create a new token
            reset.save()

            # Set email data
            template_email ='registration/password_reset_email.html'
            context = {
                'user': user,
                'protocol': request.scheme,
                'domain': request.get_host(),
                'uid': force_text(urlsafe_b64encode(force_bytes(user.pk))),
                'token': reset.token
            }
            
            message = render_to_string(template_email, context=context)
            subject = 'Recovery Password'
            from_email = EMAIL_SENDER

            # Send email
            user.email_user(subject, message, from_email)
        except User.DoesNotExist:
            pass
        # Render the password_reset_done.html page
        return render(request,'registration/password_reset_done.html')
    return render(request,'registration/password_reset_form.html')

def password_reset_confirm(request, uidb64, token):
    '''
    Verify the user id and the token to show the reset password form.
    '''
    # Decode the user id from uidb64
    user_id = int(urlsafe_b64decode(uidb64))

    # Check the token is valid
    try:
        reset = UserResetPassword.objects.get(user=user_id)
        context = {'validlink': reset.check_token(token),
                    'user': user_id}
    except UserResetPassword.DoesNotExist:
        context = {'validlink': False}

    return render(request,'registration/password_reset_confirm.html', context)

def password_reset_complete(request):
    '''
    Handle the new password form for reset.
    '''
    if request.method == 'POST':
        password = request.POST['password']
        pass_check = request.POST['pass-check']
        user_id = request.POST['user']
        
        if password == pass_check:
            try:
                user = User.objects.get(id=user_id)
                validate_password(password, user)
                user.set_password(password)
                user.save()
                response = {
                    'success': True,
                    'redirect': reverse("registration:password_reset_success")
                }
            except User.DoesNotExist:
                response = {
                    'success': False,
                    'error': 'username',
                    'message': ['An error was ocurred. Try again.'],
                    'redirect': reverse("registration:password_reset_error")
                    }
            except ValidationError as e:
                response = {
                        'success': False,
                        'error': 'credentials',
                        'message': list(e)
                        }
        else:
            response = {
                'success': False,
                'error': 'credentials',
                'msg': ['The passwords entries must be the same.']
                }
        return JsonResponse(response)
    return HttpResponseRedirect(reverse('orders:index'))

def password_reset_success(request):
    '''
    Render the Successfull Reset Password Page.
    '''
    return render(request, 'registration/password_reset_complete.html')

def password_reset_failed(request):
    '''
    Render the Error Reset Password Page for token invalid.
    '''
    return render(request, 'registration/password_reset_error.html')
