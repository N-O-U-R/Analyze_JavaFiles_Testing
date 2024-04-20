import unittest
from unittest.mock import mock_open, patch
import os
import re
from parameterized import parameterized
from django.conf import settings
from faker import Faker
import tempfile

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
        ("https://youtube.com", False),
        ("https://github.com", False),
    ])
    def test_url_pattern(self, input_url, expected):
        pattern = r'^https:\/\/github\.com\/[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\/[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$'
        result = bool(re.match(pattern, input_url))
        self.assertEqual(result, expected)

    @parameterized.expand([
        # Valid class declarations
        ("public class MyClass {}", True),
        ("public class MyClass {\n\n\n}", True),
        ("private final class MyClass {}", True),
        ("class MyClass extends BaseClass {}", True),
        ("abstract class MyClass<T> implements InterfaceOne, InterfaceTwo {}", True),
        ("class MyClass implements Interface {", True),
        ("final class MyClass extends Base implements InterfaceOne, InterfaceTwo {}", True),
        ("class MyClass<T> extends Base<T> implements InterfaceOne<T>, InterfaceTwo<T> {\n\n}", True),
        ("public class Test {}\n" + "a = 1\n" * 10000, True),
        # Invalid class declarations
        ("// class MyClass {}", False),
        ("/* class MyClass {} */", False),
        ("String text = 'public class NotAClass';", False),
        ("public enum MyEnum { VALUE1, VALUE2 }", False),
        ("interface MyInterface {}", False),
    ])
    def test_class_declarations(self, content, expected):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            result = is_class_file(tmp.name)
            self.assertEqual(result, expected)
        os.unlink(tmp.name)

    def test_non_existent_file(self):
        fake = Faker()
        non_existent_file = fake.file_path(depth=3, extension="java")
        with self.assertRaises(FileNotFoundError):
            is_class_file(non_existent_file)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.flush()
            result = is_class_file(tmp.name)
            self.assertFalse(result)
        os.unlink(tmp.name)
    
    @parameterized.expand([
        ("/** Javadoc */\npublic class MyClass {}", 1),
        ("/**\n * Javadoc comment\n */\nclass Test {}", 1),
        ("/** Start of Javadoc\n * More details\n */\nvoid method() {}", 1),
        ("/** Multiple\n * Line Javadoc\n * With various details\n */\nint x;", 2),
        ("/**/public class Empty {}", 0),  
        ("/** Javadoc */\n\nclass MultiJavadoc {}", 1),
        ("// Single line comment/** Javadoc */\npublic class MyClass {}", 0),
        ("\npublic class MyClass {}\n", 0),
        ("/** Javadoc \n /* MultiLine */ \n * \n * \n */ public class MyClass {}", 3),
        ("/* Multi-line comment \n /** Javadoc \n * \n * \n */\npublic class MyClass {}", 0),
        ("/** Javadoc \n * /** Nested */ \n */\npublic class MyClass {}", 1),
    ])
    def test_javadoc_comments(self, content, expected_count):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Javadoc Comment Lines'], expected_count)
        os.unlink(tmp.name)

    @parameterized.expand([
        ("// single line comment\npublic class MyClass {}", 1),
        ("public class MyClass {} // inline comment", 1),
        ("// comment 1\n// comment 2\nvoid method() {}", 2),
        ("void method() {} // Inline\n// Above line", 2),
        ("// First line\n//Second line\n// Third line", 3),
        ("/*\n // Nested comment\n*/class MultiComment {}", 0),
        ("/**\n * // Nested comment\n */\nclass MultiComment {}", 0),
        ("/*\n * Multi-line comment\n */\npublic class Test {}", 0),
        ("\npublic class MyClass {}\n", 0),
        ("/*\nMulti-line*/\n/**\n* Javadoc \n**/\npublic class MyClass {}", 0),
    ])
    def test_single_line_comments(self, content, expected_count):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Single-line Comment Lines'], expected_count)
        os.unlink(tmp.name)

    @parameterized.expand([
        ("/* Multi-line\n * comment\n */\nclass Test {}", 1),
        ("/* Another comment */\n/* Second comment block */\nvoid method() {}", 2),
        ("/* Start of comment\n * Continuation\n * End of comment */\nint x;", 1),
        ("/* Multi-level\n /* Nested comment */\n Still comment */\nint y;", 1),
        ("/** Javadoc comment */\n/* Multi-line comment */\npublic class MyClass {}", 1),
        ("/** \n * /* \n * Nested comment\n */\n */\nclass NestedComment {}", 0),
    ])
    def test_multi_line_comments(self, content, expected_count):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Multi-line Comment Lines'], expected_count)
        os.unlink(tmp.name)

    @parameterized.expand([
        ("public class MyClass {}", 1),
        ("public int add(int a, int b) { return a + b; }", 1),
        ("void setup() {}\nvoid teardown() {}", 2),
        ("// Comment\npublic int x;\nint y; // Comment", 2),
        ("\n\npublic void doNothing() {}\n", 1),
        ("public class Test // Comment\n{\n\n}", 3),
        ("public void method() {} // Comment", 1),
        ("public int add(int a, int b) { return a + b; } /* Comment */", 1),
        ("public class ClassName {} /** Comment */", 1),
    ])
    def test_code_lines(self, content, expected_count):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Code Lines'], expected_count)
        os.unlink(tmp.name)

    @parameterized.expand([
        ("public void myMethod() {}", 1),
        ("private static int compute() { return 0; }", 1),
        ("public void myMethod() \n{\n}", 1),
        ("public class MyClass { void method1() {} void method2() {} }", 2),
        ("public class MyClass {\n\npublic void method1() {}\n\npublic void method2() {}\n}", 2),
        ("public class MyClass { void method1() {} void method2() {} void method3() {} }", 3),
    ])
    def test_function_counting(self, content, expected_functions):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Function Count'], expected_functions)
        os.unlink(tmp.name)

    @parameterized.expand([
        ("public class MyClass {}", 1),
        ("public class MyClass {\n}", 2),
        ("\n\n\n", 3),
        ("// Comment\n\nint x;\n", 3),
        ("/** Javadoc\n * More info\n */\nclass Test {}", 4),
    ])
    def test_total_lines(self, content, expected_loc):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Total Lines (LOC)'], expected_loc)
        os.unlink(tmp.name)


    def test_large_random_content(self):
        fake = Faker()
        comments = "\n".join([f"// {fake.sentence()}" for _ in range(1000)])  # 100 single-line comments
        code_blocks = "\n".join([f"public void method{_}() {{ \nSystem.out.println(); }}" for _ in range(500)])  # 50 methods
        content = f"{comments}\n{code_blocks}"
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Single-line Comment Lines'], 1000)
            self.assertEqual(results['Function Count'], 500)
            self.assertEqual(results['Code Lines'], 1000)  
        os.unlink(tmp.name)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Total Lines (LOC)'], 0)
        os.unlink(tmp.name)

    def test_file_without_functions(self):
        content = "// This is a comment\n/* Another comment */"
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Function Count'], 0)
        os.unlink(tmp.name)
        
    def test_comment_deviation_percentage_with_no_functions(self):
        content = """
        // single-line comment
        /*
        * Multi-line comment
        */
        // single-line comment
        """
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(content)
            tmp.flush()
            results = analyze_java_file(tmp.name)
            self.assertEqual(results['Comment Deviation Percentage'], -100)
        os.unlink(tmp.name)
    