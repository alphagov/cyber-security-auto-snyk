# cyber-security-auto-snyk
Automate running snyk test across alphagov repos offline and aggregate JSON results to prioritise action

The app uses python  Fire and runs from the command
line. 

**This is work in progress at an experimental phase 
and does not necessarily all work yet**

## Setup

* Create a GitHub [Personal Access Token](https://github.com/settings/tokens)
* Create a python >3.6 virtual env and activate
* `pip install -r requirements.txt`

## Authenticate as your GitHub user

To read the organisation teams and member repos 
the API needs user level authentication. 

export AUTOSNYK_USER=[github_user_name]
export AUTOSNYK_TOKEN=[github_access_token] 

## Options 

`python app.py [method] [arg1, arg2..]`
* Audit `.. app.py audit alphagov`
* Test a team `.. app.py test alphagov team-name`
* Cleanup repos `.. app.py tidy alphagov team-name`
* Reset `.. app.py reset alphagov team-name`

