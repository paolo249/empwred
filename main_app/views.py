from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Activity, Log
from .forms import LogForm
import requests
import os

# Create your views here.

def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def dashboard(request):
  key = os.environ['ZEN_API_KEY']
  quote = requests.get(f'https://zenquotes.io/api/today/{key}').json()
  print(quote)
  categories = Category.objects.all()
  return render(request, 'categories/index.html', { 'categories': categories, 'html': quote[0]['h'] })  

class ActivityCreate(CreateView):
  model = Activity
  fields = ['title', 'description', 'categories']
  # will be called if the activity data is valid
  def form_valid(self, form):
    # form.instance is the in-memory new activity obj
    form.instance.user = self.request.user
    # Let the CreateView's form_valid method do its job
    return super().form_valid(form)

class ActivityUpdate(UpdateView):
  model = Activity
  fields = ['title', 'description', 'categories']

class ActivityDelete(DeleteView):
  model = Activity
  success_url = '/dashboard/'

def activity_list(request):
  category = request.GET.get('category')
  if category:
    activities = Activity.objects.filter(user=request.user, categories__title=category)
  else:
    activities = Activity.objects.filter(user=request.user)
  return render(request, 'activities/index.html', { 'activities': activities, 'category': category })

def activity_detail(request, activity_id):
  activity = Activity.objects.get(id=activity_id)
  log_form = LogForm()
  return render(request, 'activities/detail.html', {
    'activity': activity,
    'log_form': log_form,
  })

def add_log(request, activity_id):
  # create a ModelForm instance using the data in the posted form
  form = LogForm(request.POST)
  # validate the data
  if form.is_valid():
    new_log = form.save(commit=False)
    new_log.activity_id = activity_id
    new_log.save()
  return redirect('activity_detail', activity_id=activity_id)

def delete_log(request, activity_id, log_id):
  Log.objects.filter(id=log_id).delete()
  return redirect('activity_detail', activity_id=activity_id)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

  