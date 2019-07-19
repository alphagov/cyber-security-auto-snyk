import os
import shutil
from datetime import datetime, timezone
from .github_auditor import GithubAuditor

class Snyker():
    """
    Install snyk into local clones
    TODO Recursively search repos for common dependency files
    Cleanup: git reset --hard
    """

    def __init__(self):
        """
        Create a github_auditer instance
        """
        self.github_auditor = GithubAuditor()

    def test(self, org_name, team_slug):

        return_to = os.getcwd()
        checkout_into = f"repos/{org_name}/{team_slug}"

        repos = self.github_auditor.clone_team_repos(org_name, team_slug)
        os.chdir(checkout_into)

        for repo in repos:
            self._test_repo(repo)
        os.chdir(return_to)
        # self.github_auditor.empty_team_repos(org_name, team_slug)

    def audit(self, org_name):

        teams = self.github_auditor.get_org_teams(org_name)

        for team in teams:
            team_slug = team.slug
            self._audit_team(org_name, team)

    def _audit_team(self, org_name, team):

        return_to = os.getcwd()
        checkout_into = f"repos/{org_name}/{team_slug}"
        os.chdir(checkout_into)
        team_slug = team.slug
        print(f"{org_name}: {team_slug}")

        repos = self.github_auditor.clone_team_repos(org_name, team_slug)
        for repo in repos:
            print(f" -- {repo.name}")
            self._test_repo(repo)

        os.chdir(return_to)
        self.tidy(org_name, team_slug)

    def tidy(self, org_name, team_slug):
        self.github_auditor.empty_team_repos(org_name, team_slug)

    def reset(self, org_name, team_slug):
        self.tidy(org_name, team_slug)
        self._delete_results(org_name, team_slug)

    def _delete_results(self, org_name, team_slug):
        shutil.rmtree(f"results/{org_name}/{team_slug}")

    def _test_repo(self, repo):

        os.chdir(repo.name)
        here = os.getcwd()

        self._install()
        self._recursive_dependency_search(here)

        os.chdir("..")

    def _install(self):
        os.system("npm install snyk")

    def _run(self):

        here = os.getcwd()
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        save_into = f"{here}/{today}".replace("repos", "results")

        os.makedirs(save_into, exist_ok=True)
        os.system(f"snyk test --json > {save_into}/snyk_test.json")

    def _get_dependency_files(self):
        dependency_files = {
            "requirements.txt": "python",
            "requirements-dev.txt": "python",
            "package.json": "npm",
            "Gemfile": "ruby",
            "bower.json": "bower",
            "composer.json": "composer",
            "pom.xml": "maven"
        }
        return dependency_files

    def _prepare_python(self, file):
        print(f"Install python requirements file: {file}")
        os.system(f"pip install -r {file}")
        return True

    def _prepare_npm(self, file):

        here = os.getcwd()

        # don't run snyk against dependency package.json files
        is_package = "node_modules" in here
        if is_package:
            print(f"Ignoring package dependencies in: {here}")
        else:
            os.system(f"npm install")
        return not is_package

    def _prepare(self, lang, file):

        prepare_langs = {
            "python": self._prepare_python,
            "npm": self._prepare_npm
        }

        if lang in prepare_langs:
            prepared = prepare_langs[lang](file)
        else:
            prepared = True

        return prepared

    def _record(self, lang, file):
        here = os.getcwd()
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        save_into = f"{here}/{today}".replace("repos", "results")
        os.makedirs(save_into, exist_ok=True)
        shutil.copyfile(file, save_into)

    def _recursive_dependency_search(self, path):

        return_to = os.getcwd()
        dependency_files = self._get_dependency_files()
        dependency_filenames = dependency_files.keys()

        #for sub_directory in os.walk(path):
        for file in os.listdir(path):
            if os.path.isdir(f"{path}/{file}"):
                self._recursive_dependency_search(f"{path}/{file}")
            else:
                if file in dependency_filenames:
                    lang = dependency_files[file]
                    os.chdir(path)
                    print(f"{path} contains a dependency file: {file} of type: {lang}")

                    self._record(lang, file)

                    # prepared = self._prepare(lang, file)
                    # if prepared:
                    #     self._run()

                    os.chdir(return_to)

        return True
