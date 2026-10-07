from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# django-allauth, package that ships ready-made views, templates, and URLS for login, signup, password reset 
# and email verification

# The manual login built
def login_view(request):
    if request.method == "POST":    
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Verify credentials against cryptographic hashes in the database
        user = authenticate(request, username=username,  password=password)

        if user is not None:
            login(request,  user) #Attaches session ID to request
            return redirect("/")

    return render(request, "off/login.html")    
