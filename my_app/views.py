from django.shortcuts import render, redirect
from my_app.forms import RepoURLForm
from .models import Repository, JavaDosyasi
from my_app.services.repo_analyzer import repo_analyzer ,delete_repo, delete_all_repos

def home(request):
    if request.method == 'POST':
        form = RepoURLForm(request.POST)
        if 'analyze' in request.POST and form.is_valid():
            repo_url = form.cleaned_data['repo_url']
            repo_analyzer(repo_url)
            return redirect('repo_details', repo_url=repo_url)
    elif 'delete_all' in request.GET:
        delete_all_repos()
    elif 'delete' in request.GET:
        repo_url = request.GET['delete']
        delete_repo(repo_url)

    form = RepoURLForm()
    repositories = Repository.objects.all()
    return render(request, 'my_app/index.html', {'form': form, 'repositories': repositories})



def repo_details(request, repo_url):
    repository = Repository.objects.get(url=repo_url)
    java_files = JavaDosyasi.objects.filter(depo_id = repository.id)
    return render(request, 'my_app/repo_details.html', {'repository': repository, 'java_files': java_files})
