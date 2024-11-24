from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from main.forms import CustomUserCreationForm
from main.views.views import get_base_context


def login_page(request):
    if request.method == "POST":
        print(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Авторизация успешна")
        else:
            messages.add_message(
                request, messages.ERROR, "Неправильный логин или пароль"
            )
    return redirect("index")


def registration_page(request):
    context = get_base_context(request)

    if request.method == "POST":
        reg_form = CustomUserCreationForm(request.POST)
        if reg_form.is_valid():
            reg_form.save()

            username = reg_form.cleaned_data.get("username")
            password = reg_form.cleaned_data.get("password1")
            email = reg_form.cleaned_data.get("email")

            user = authenticate(username=username, password=password, email=email)
            login(request, user)

            return redirect("index")

        context["reg_form"] = CustomUserCreationForm()
        data_errors = reg_form.errors.get_json_data()
        for _item in data_errors["password2"]:
            messages.add_message(request, messages.ERROR, _item["message"])
        return render(request, "registration/registration.html", context)

    reg_form = CustomUserCreationForm()

    context["reg_form"] = reg_form
    return render(request, "registration/registration.html", context)
