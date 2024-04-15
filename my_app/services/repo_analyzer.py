import shutil
from my_app.services.repo_cloner import repo_cloner 
from my_app.services.java_analyzer import analyze_java_files_in_directory 

def repo_analyzer(repo_url):
    destination = repo_cloner(repo_url) 
    analyze_java_files_in_directory(destination, repo_url)
    try:
        shutil.rmtree(destination)
    except Exception as e:
        print(f"Error removing directory {destination}: {e}")

