import os
import django
django.setup()
from my_app.models import Repository, JavaDosyasi
from django.utils.timezone import now

def is_class_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        if "class" in content:
            return True
    return False

def analyze_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    javadoc_comments, single_line_comments, multi_line_comments = 0, 0, 0
    code_lines, total_lines = 0, len(lines)
    functions = 0
    in_javadoc_comment, in_multi_line_comment = False, False

    for line in lines:
        stripped_line = line.strip()
        if in_javadoc_comment:
            javadoc_comments += 1
            if stripped_line.endswith("*/"):
                in_javadoc_comment = False
                javadoc_comments -= 1  # Do not count the closing tag of Javadoc
            continue
        elif stripped_line.startswith("/**"):
            in_javadoc_comment = True
            continue  # Skip the opening of Javadoc comments
        elif in_multi_line_comment:
            multi_line_comments += 1
            if stripped_line.endswith("*/"):
                in_multi_line_comment = False
                multi_line_comments -= 1  # Do not count the closing tag of multiline comments
            continue
        elif stripped_line.startswith("/*"):
            in_multi_line_comment = True
            continue  # Skip the opening of multiline comments

        if "//" in stripped_line:  # Check for inline single-line comments
            single_line_comments += 1
            if not stripped_line.startswith("//"):  # Count as code if not only a comment
                code_lines += 1
            continue

        if stripped_line and not stripped_line.startswith("//"):
            code_lines += 1
            if (" public " in stripped_line or stripped_line.startswith("public ") or
                " private " in stripped_line or stripped_line.startswith("private ") or
                " protected " in stripped_line or stripped_line.startswith("protected ") or
                " static " in stripped_line or stripped_line.startswith("static ")) and "(" in stripped_line and ")" in stripped_line and "{" in stripped_line:
                functions += 1

    total_comments = javadoc_comments + single_line_comments + multi_line_comments
    loc = total_lines

    if functions > 0:
        yg = ((javadoc_comments + single_line_comments + multi_line_comments) * 0.8) / functions
        yh = (code_lines / functions) * 0.3
        comment_deviation_percentage = ((100 * yg) / yh) - 100
    else:
        comment_deviation_percentage = -100

    return {
        'Javadoc Comment Lines': javadoc_comments,
        'Single-line Comment Lines': single_line_comments,
        'Multi-line Comment Lines': multi_line_comments,
        'Code Lines': code_lines,
        'Total Lines (LOC)': loc,
        'Function Count': functions,
        'Comment Deviation Percentage': comment_deviation_percentage,
    }


def analyze_java_files_in_directory(directory_path, repo_url):
    repository, created = Repository.objects.get_or_create(url=repo_url)
    if not created:
        repository.java_dosyalari.all().delete()
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".java") and is_class_file(os.path.join(root, file)):
                file_path = os.path.join(root, file)
                analysis_results = analyze_java_file(file_path)
                JavaDosyasi.objects.create(
                    depo=repository,
                    sinif_adi=file,
                    javadoc_yorum_satir_sayisi=analysis_results['Javadoc Comment Lines'],
                    yorum_satir_sayisi=analysis_results['Single-line Comment Lines'] + analysis_results['Multi-line Comment Lines'],
                    kod_satir_sayisi=analysis_results['Code Lines'],
                    toplam_satir_sayisi=analysis_results['Total Lines (LOC)'],
                    fonksiyon_sayisi=analysis_results['Function Count'],
                    yorum_sapma_yuzdesi=analysis_results['Comment Deviation Percentage'],
                )
    print(f"All files in {repo_url} have been analyzed and saved to the database.")


