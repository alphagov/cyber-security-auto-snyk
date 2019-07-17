import sys
import os
from github3 import GitHub
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization



class GithubAuditor():
    """
    Implements Github3py client and manages connections and credentials
    """

    def __init__(self):
        self.load_app_credentials()
        self.github = GitHub()
        # TODO Can we use client credentials somehow with something like the below?
        print(f"Connecting to API as app: {self.app_id}")
        self.github.login_as_app_installation(
            self.pem_bytes,
            self.app_id,
            self.install_id
        )

    def load_app_credentials(self):
        """
        Load credentials defined in environment variables
        """
        if "AUTOSNYK_APP" in os.environ:
            self.app_id = int(os.environ["AUTOSNYK_APP"])

        if "AUTOSNYK_INSTALL" in os.environ:
            self.install_id = int(os.environ["AUTOSNYK_INSTALL"])

        if "AUTOSNYK_KEY" in os.environ:
            key_path = os.environ["AUTOSNYK_KEY"]
            with open(key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
                self.pem_bytes = self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

                # self.private_key = key_file.read()
                print("Key file is x bytes: " + str(sys.getsizeof(self.private_key)))
                print("Key pem is x bytes: " + str(sys.getsizeof(self.pem_bytes)))

        print(f"Loaded credentials for app: {self.app_id}")

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
        for team in teams:
            print(team.as_json())
