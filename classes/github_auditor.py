import sys
import os
import shutil

from github3 import GitHub
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization



class GithubAuditor():
    """
    Implements Github3py client and manages connections and credentials
    """

    def __init__(self):
        self.load_app_credentials()
        # self.github = GitHub()
        self.github = GitHub(self.user, token=self.token)
        # TODO Can we use client credentials somehow with something like the below?
        # print(f"Connecting to API as app: {self.app_id}")
        # self.github.login_as_app_installation(
        #     self.private_key_bytes,
        #     self.app_id,
        #     self.install_id
        # )

    def load_app_credentials(self):
        """
        Load credentials defined in environment variables
        """
        if "AUTOSNYK_APP" in os.environ:
            self.app_id = int(os.environ["AUTOSNYK_APP"])

        if "AUTOSNYK_INSTALL" in os.environ:
            self.install_id = int(os.environ["AUTOSNYK_INSTALL"])

        if "AUTOSNYK_USER" in os.environ:
            self.user = os.environ["AUTOSNYK_USER"]

        if "AUTOSNYK_TOKEN" in os.environ:
            self.token = os.environ["AUTOSNYK_TOKEN"]

        if "AUTOSNYK_KEY" in os.environ:
            key_path = os.environ["AUTOSNYK_KEY"]
            with open(key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
                self.private_key_bytes = self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

    def usage(self):
        say = "python app.py get_repos [org_name]"
        print(self.github.octocat(say))

    def get_repos(self, org_name):
        print(f"get_repos for {org_name}")
        by_status = {
            "open": [],
            "private": []
        }
        for repo in self.github.repositories_by(org_name):
            # print(repo.as_json())
            # print(repo.name)
            if repo.private:
                by_status["private"].append(repo)
            else:
                by_status["open"].append(repo)

        for status, repos in by_status.items():
            count = str(len(repos))
            print(f"{status}: {count}")

    def get_org(self, org_name):
        org = self.github.organization(org_name)
        return org

    def get_org_teams(self, org_name):
        org = self.get_org(org_name)
        teams = org.teams()
        # for team in teams:
        #     #print(team.as_json())
        #     print(team.slug)
        return teams

    def get_team_repos(self, org_name, team_slug):
        teams = self.get_org_teams(org_name)
        repos = []
        for team in teams:
            if team.slug == team_slug:
                repos = team.repositories()
        return repos

    def list_team_repos(self, org_name, team_slug):
        repos = self.get_team_repos(org_name, team_slug)
        for repo in repos:
            print(repo.name)

    def clone_team_repos(self, org_name, team_slug):
        initial_directory = os.getcwd()
        repos = self.get_team_repos(org_name, team_slug)
        checkout_into = f"repos/{org_name}/{team_slug}"
        os.makedirs(checkout_into, exist_ok=True)
        cloned = []
        for repo in repos:
            is_checked_out = os.path.exists(f"{checkout_into}/{repo.name}")
            if not repo.private:
                # if it's already there make sure it's current
                if is_checked_out:
                    os.chdir(checkout_into)
                    print(os.getcwd())
                    # os.system("git reset --hard origin/master")
                    # os.system("git pull")
                    os.chdir(initial_directory)
                else:
                    self.clone_repo(repo, checkout_into)
                cloned.append(repo)
        return cloned

    def clone_repo(self, repo, checkout_into):
        clone_url = repo.clone_url
        print(clone_url)
        return_to = os.getcwd()
        os.chdir(checkout_into)
        os.system(f"git clone {clone_url}")
        os.chdir(return_to)

    def empty_team_repos(self, org_name, team_slug):
        checkout_into = f"repos/{org_name}/{team_slug}"
        #os.removedirs(checkout_into)
        shutil.rmtree(checkout_into)

    def say(self, text):
        self.github.octocat(say=text)

