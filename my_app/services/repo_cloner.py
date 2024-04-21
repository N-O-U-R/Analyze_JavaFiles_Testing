import os
import git
import sys
import re
import logging
current_script_path = os.path.abspath(__file__)
project_root = os.path.join(current_script_path, os.pardir, os.pardir, os.pardir)

sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Odev1.settings')

import django
django.setup()

from django.conf import settings
def repo_cloner(repo_url):
    url_pattern = r'^https:\/\/github\.com\/[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\/[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$'
    if not re.match(url_pattern, repo_url):
        return "Invalid URL. Please provide a valid GitHub URL."
    
    os.makedirs(settings.CLONED_REPOS_DIR, exist_ok=True)
    destination = os.path.join(settings.CLONED_REPOS_DIR, repo_url.split('/')[-1])
    try:
        if os.path.exists(destination) and os.path.isdir(destination):
            logging.info("This repository has already been cloned")
        else:
            git.Repo.clone_from(repo_url, destination)
            logging.info("Repository cloned successfully!")
    except Exception as e:
        error_message = str(e)
        if 'fatal: repository' in error_message and 'not found' in error_message:
            return "Repository not found. Please check the provided repository URL."
        else:
            return "An error occurred while cloning the repository."
    
    return destination


# Example usage
# repo_url = 'https://github.com/mfadak/Odev1Ornek'
# repo_cloner(repo_url)
