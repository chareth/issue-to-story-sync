# issue-to-story-sync

Python Flask app to create stories on Pivotal Tracker from issues on GitHub. The frequency of how often the app runs can be configured,
along with which organizations' repositories to pull from and where to post the issues. Stories will be tagged with the name of the repo and the specified epic name.


## Install

### Requirements

* [virutalenv](https://pypi.python.org/pypi/virtualenv)

### Steps
1. `virtualenv issue-sync-venv`
2. Activate the virtual env:  
For *nix: `source issue-sync-venv/bin/activate`  
For Windows: `source issue-sync-venv/Scripts/activate`
3. Run `pip install -r requirements.txt` to install required packages.
4. Create a local config json file
5. Set environment variables:  
  `CONFIG_NAME=<name of config file>`
6. To run the app: `python run.py`


### Config  
The config file is a json file that should contain the following attributes:
```
{
  "GITHUB_API_KEY": "0000000000000000000000",
  "PTRACKER_API_KEY": "0000000000000000000000",
  "GITHUB_BASE_URL": "https://github.homedepot.com/api/v3/"
  "PTRACKER_BASE_URL": "https://www.pivotaltracker.com/services/v5/"
  "INTERVAL": "24"
  "ORG_PROJECT_INFO": [
    {
      "ORG": ["OrgA"],
      "PROJECT_ID": ["111"],
      "EPIC_NAME": "issues"
    }
  ]
}
```
Property name | Value | Description
---|---|---
GITHUB_API_KEY | string | key to access GitHub API
PTRACKER_API_KEY | string | key to access Pivotal Tracker API
GITHUB_BASE_URL | string | base url to GitHub API
PTRACKER_BASE_URL | string | base url to Pivotal Tracker API
INTERVAL | string | how often the app runs in hours
ORG_PROJECT_INFO | array | array of GitHub organization to PivotalTracker project pairings  

#### GitHub organization to PivotalTracker project pairings
```
{
  "ORG": ["OrgA"],
  "PROJECT_ID": ["111"],
  "EPIC_NAME": "issues"
}
``` 
Property name | Value | Description
---|---|---
ORG | array | string array of GitHub organization names
PROJECT_ID | array | string array of PivotalTracker board ids
EPIC_NAME | string | name of epic that issues should be under

The 'ORG_PROJECT_INFO' is a list of GitHub organization to PivotalTracker project pairings. The way the object is 
set up allows for a one to one, many to one, one to many, or many to many relationship between an organization and project.

#### One to One  
```
{
  "ORG": ["OrgA"],
  "PROJECT_ID": ["111"],
  "EPIC_NAME": "issues"
}
```  
All the issues in the repos that OrgA has will go to project 111 in the "issues" epic.

#### Many to One  
```
{
  "ORG": ["OrgA", "OrgB", "OrgC"],
  "PROJECT_ID": ["111"],
  "EPIC_NAME": "issues"
}
```  
All the issues from the repos of OrgA, OrgB and OrgC will be created as stories in project 111 in the "issues" epic.

#### One to Many  
```
{
  "ORG": ["OrgA"],
  "PROJECT_ID": ["111", "222", "333"],
  "EPIC_NAME": "issues"
}
```  
All the issues from the repos of OrgA  will be created as stories in project 111, 222, and 333 in the "issues" epic of each project.

#### Many to Many  
```
{
  "ORG": ["OrgA", "OrgB", "OrgC"],
  "PROJECT_ID": ["111", "222"],
  "EPIC_NAME": "issues"
}
```  
All the issues from the repos of OrgA, OrgB and OrgC will be created as stories in project 111 and 222 in the "issues" epic of each project.

## Endpoints

#### /
Prints the scheduled jobs and when they will run.

#### /sync
Create a job to run now. The daily job will still run at the normally scheduled time.

## Deploy
This app is deployed on PCF. To deploy on PCF:  
1. `python setup.py bdist_wheel`  
2. `cf push` in the root directory  

