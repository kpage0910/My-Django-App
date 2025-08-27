from django.shortcuts import render

def home(request):
    context = {
        'title': 'Welcome to My Site',
        'message': 'Hello from Django!'
    }
    return render(request, 'myapp/home.html', context)

def about(request):
    context = {
        'title': 'About Us',
    }
    return render(request, 'myapp/about.html', context)