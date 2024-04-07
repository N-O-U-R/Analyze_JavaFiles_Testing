from repo_cloner import repo_cloner 
from java_analyzer import analyze_java_files_in_directory 

def main():
    repo_url = input("Enter the GitHub repository URL to clone and analyze: ")
    destination = repo_cloner(repo_url) 
    analyze_java_files_in_directory(destination, repo_url)

if __name__ == "__main__":
    main()
