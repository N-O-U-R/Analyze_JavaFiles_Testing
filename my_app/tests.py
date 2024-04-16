import unittest
import os
from my_app.services.repo_cloner import repo_cloner
from my_app.services.java_analyzer import analyze_java_file
from my_app.services.java_analyzer import is_class_file
from my_app.services.java_analyzer import analyze_java_files_in_directory


class RepoAnalyzerTest(unittest.TestCase):
    def test_repo_cloner(self):
        repo_url = 'https://github.com/mfadak/Odev1Ornek'
        base_path = os.getcwd()
        expected_path = os.path.join(base_path, 'cloned_repos', 'Odev1Ornek')
        if os.path.exists(expected_path) and os.path.isdir(expected_path):
            self.assertEqual(repo_cloner(repo_url), "This repository has already been cloned")
        else:
            self.assertEqual(repo_cloner(repo_url), expected_path)

    # Parameterized test example comes here
    def test_repo_cloner_with_invalid_url(self):
        repo_url = 'https://invalid_url.com/mfadak/Odev1Ornek'
        self.assertEqual(repo_cloner(repo_url), "Invalid URL. Please provide a valid GitHub URL.")

    # def test_is_class_file(self):
        # Use Mock or write a file to test the function
        # self.assertTrue(is_class_file("my_app/services/java_analyzer.py"))
        # self.assertFalse(is_class_file("my_app/tests.py"))