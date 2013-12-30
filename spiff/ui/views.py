from django.shortcuts import render

def partial(request, name):
  return render(request, name)
