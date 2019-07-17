import os
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

        os.chdir(return_to)
        # self.github_auditor.empty_team_repos(org_name, team_slug)

    def test_repo(self, repo):
        os.chdir(repo.name)
        os.system("npm install snyk")
        os.system("snyk test --json > snyk_test.json")
        os.chdir("..")