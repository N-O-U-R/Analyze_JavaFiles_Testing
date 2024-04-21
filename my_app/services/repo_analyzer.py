import shutil
import os
import stat
from my_app.services.repo_cloner import repo_cloner 
from my_app.services.java_analyzer import analyze_java_files_in_directory
from my_app.models import Repository 

def remove_readonly(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWRITE)
    func(path)

def repo_analyzer(repo_url):
    destination = repo_cloner(repo_url) 
    analyze_java_files_in_directory(destination, repo_url)
    try:
        shutil.rmtree(destination, onerror=remove_readonly)
        print(f"Removed repo {destination}")
    except Exception as e:
        print(f"Error removing directory {destination}: {e}")

def delete_repo(repo_url):
    try:
        repo = Repository.objects.get(url=repo_url)
        repo.delete()
        return True
    except Repository.DoesNotExist:
        return False

def delete_all_repos():
    Repository.objects.all().delete()

