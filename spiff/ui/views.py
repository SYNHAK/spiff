from django.shortcuts import render

def index(request):
  return render(request, 'ui/index.html')

def partial(request, name):
  return render(request, 'ui/'+name)
