import unittest
import os
import re
from parameterized import parameterized
from django.conf import settings
from faker import Faker
from my_app.services.repo_cloner import repo_cloner
from my_app.services.java_analyzer import analyze_java_file
from my_app.services.java_analyzer import is_class_file
from my_app.services.java_analyzer import analyze_java_files_in_directory


class RepoAnalyzerTest(unittest.TestCase):
    def test_valid_github_url(self):
        repo_url = 'https://github.com/mfadak/Odev1Ornek'
        expected_destination = os.path.join(settings.CLONED_REPOS_DIR, 'Odev1Ornek')
        result = repo_cloner(repo_url)
        self.assertEqual(result, expected_destination)
        self.assertTrue(os.path.exists(expected_destination))

    def test_invalid_github_url(self):
        fake = Faker()
        invalid_url = fake.uri()  
        result = repo_cloner(invalid_url)
        self.assertEqual(result, "Invalid URL. Please provide a valid GitHub URL.")

    def test_repo_already_cloned(self):
        repo_url = 'https://github.com/mfadak/Odev1Ornek'
        destination = os.path.join(settings.CLONED_REPOS_DIR, 'Odev1Ornek')
        os.makedirs(destination, exist_ok=True)  
        with self.assertLogs(level='INFO') as log:
            result = repo_cloner(repo_url)
            self.assertTrue(any("This repository has already been cloned" in message for message in log.output))
        self.assertEqual(result, destination)


    @parameterized.expand([
        ("https://github.com/user/repo", True),
        ("https://github.com/user-name/repo-name", True),
        ("https://github.com/user/repo/subdir", False),
        ("http://github.com/user/repo", False),
        ("https://gitlab.com/user/repo", False),
    ])
    def test_url_pattern(self, input_url, expected):
        pattern = r'^https:\/\/github\.com\/[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\/[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$'
        result = bool(re.match(pattern, input_url))
        self.assertEqual(result, expected)

    

    # def test_is_class_file(self):
        # Use Mock or write a file to test the function
        # self.assertTrue(is_class_file("my_app/services/java_analyzer.py"))
        # self.assertFalse(is_class_file("my_app/tests.py"))

        