import os
import git
import sys

# Calculate the path to the project root dynamically
current_script_path = os.path.abspath(__file__)
project_root = os.path.join(current_script_path, os.pardir, os.pardir, os.pardir)

# Adjust the system path
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Odev1.settings')

import django
django.setup()

from django.conf import settings
def repo_cloner(repo_url):
    os.makedirs(settings.CLONED_REPOS_DIR, exist_ok=True)
    destination = os.path.join(settings.CLONED_REPOS_DIR, repo_url.split('/')[-1])
    if os.path.exists(destination) and os.path.isdir(destination):
        print("This repository has already been cloned.")
    else:
        git.Repo.clone_from(repo_url, destination)
        print("Repository cloned successfully!")
    return destination

# Example usage
# repo_url = 'https://github.com/mfadak/Odev1Ornek'
# repo_cloner(repo_url)
