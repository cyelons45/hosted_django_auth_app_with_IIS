from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo/home.html')


def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('current')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('current')


@login_required
def current(request):
    todo = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/current.html', {'todos': todo})


@login_required
def completedtodos(request):
    todo = Todo.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos': todo})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'iform': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('current')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'iform': form, 'error': "Wrong value supplied"})


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'nform': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('current')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'nform': TodoForm(), 'error': 'Bad data passed'})


def signupuser(request):
    print()
    if request.method == 'GET':
        return render(request, 'todo/signup.html', {'form': UserCreationForm()})
    if request.POST['password1'] == request.POST['password2']:
        try:
            user = User.objects.create_user(
                username=request.POST['username'], password=request.POST['password1'])
            user.save()
            login(request, user)
            return redirect('home')
        except IntegrityError:
            return render(request, 'todo/signup.html', {'form': UserCreationForm(), 'error': "User already exist"})

    else:
        print({'message': "Passwords didn't match"})
        return render(request, 'todo/signup.html', {'form': UserCreationForm(), 'error': "Passwords did not match"})


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/login.html', {'form': AuthenticationForm()})
    user = authenticate(
        request, username=request.POST['username'], password=request.POST['password'])
    if user is None:
        return render(request, 'todo/login.html', {'form': AuthenticationForm(), 'error': "Incorrect username or password"})
    login(request, user)
    return redirect('home')
