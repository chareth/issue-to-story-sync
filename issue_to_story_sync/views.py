from issue_to_story_sync import application as app
from issue_to_story_sync import scheduler
from flask import render_template
import json
import requests
import cStringIO


@app.route('/')
def index():
    return job_info()


@app.route('/sync')
def add_job_now():
    create_jobs('sync_now', 'sync_job_now')
    return job_info()


# split up list of org to project sets into separate jobs
def create_jobs(name, job_id=None, trigger=None, next_run_time=None):

    args = {'name': name, 'func': sync_issues, 'id': job_id, 'replace_existing': True}

    if next_run_time:
        args['next_run_time'] = next_run_time
    if trigger:
        args['trigger'] = trigger

    job_num = 0
    for relation in app.config['ORG_PROJECT_INFO']:
        args['args'] = [relation]
        args['id'] += str(job_num)
        scheduler.add_job(**args)
        job_num += 1


def sync_issues(relation):
    header = {'Content-Type': 'application/json', 'Authorization': "token " + app.config['GITHUB_API_KEY']}

    try:
        # pull issues from all orgs in one ORG_PROJECT_INFO obj
        for org in relation['ORG']:

            req = requests.get(app.config['GITHUB_BASE_URL']+'orgs/' + org + '/' + 'repos', headers=header)
            repo_info = req.json()
            repo_names = [x['name'] for x in repo_info]
            for repo in repo_names:

                req_issues_closed = get_all_issues({'url': app.config['GITHUB_BASE_URL'] + 'repos/' + org + '/' + repo + '/issues',
                                            'params': {'state': 'closed', 'since': '2017-01-01'}, 'headers': header})
                req_issues_open = get_all_issues({'url': app.config['GITHUB_BASE_URL'] + 'repos/' + org + '/' + repo + '/issues',
                                            'headers': header})

                for issue in req_issues_open:
                    # don't make a story for a PR
                    if 'pull_request' not in issue:
                        story = make_story(issue, relation['EPIC_NAME'], repo)
                        # post each issue to every project board
                        for board in relation['PROJECT_ID']:
                            epic_exist(board, relation['EPIC_NAME'])
                            if not issue_exist(issue['html_url'], board):
                                post_story(story, board)

                # close stories in ptracker if the issue in gh is closed
                for issue in req_issues_closed:
                    if 'pull_request' not in issue:
                        for board in relation['PROJECT_ID']:
                            story_id = issue_exist(issue['html_url'], board)
                            if story_id is not False:
                                close_story(board, story_id)


    except requests.ConnectionError as e:
        print e.message


# check if the epic with name EPIC_NAME exists in the board
def epic_exist(tracker_project_id, epic_name):
    query_header = dict({'Content-Type': 'application/json', 'X-TrackerToken': app.config['PTRACKER_API_KEY']})
    query_req = requests.get(
        app.config['PTRACKER_BASE_URL'] + 'projects/' + str(tracker_project_id) + '/epics',
        headers=query_header).json()
    if len(filter(lambda x: x['name'] == epic_name, query_req)) == 0:
        new_epic = {'name': epic_name}
        post = requests.post(app.config['PTRACKER_BASE_URL'] + 'projects/' + str(tracker_project_id) + '/epics', data=json.dumps(new_epic), headers=query_header)
        return post.status_code


# requests all issues handling pagination
def get_all_issues(req_args):
    page = 1
    if 'params' not in req_args:
        req_args['params'] = {}
    req_args['params']['page'] = page
    req_args['params']['per_page'] = 100
    result = []

    req = requests.get(**req_args).json()
    result += req
    while len(req) >= 100:
        page += 1
        req_args['params']['page'] = page
        req = requests.get(**req_args).json()
        result.append(req)

    return result


# check if the issue is in the pivotal tracker board
def issue_exist(issue_url, tracker_project_id):
    query_header = dict({'Content-Type': 'application/json', 'X-TrackerToken': app.config['PTRACKER_API_KEY']})
    query_req = requests.get(app.config['PTRACKER_BASE_URL'] + 'projects/' + str(tracker_project_id) + '/search?query="' + issue_url + '"', headers=query_header).json()
    if query_req['stories']['total_hits'] > 0:
        return query_req['stories']['stories'][0]['id']
    return False


def make_story(issue, epic_name, repo_name):
    story = {
        'name': issue['title'],
        'labels': [epic_name, repo_name],
        'description': issue['html_url'] + '\n\n' + issue['body'],
        'current_state': 'unscheduled'
    }
    return story


def post_story(story, tracker_project_id):
    post_header = dict({'Content-Type': 'application/json', 'X-TrackerToken': app.config['PTRACKER_API_KEY']})
    story_post = requests.post(app.config['PTRACKER_BASE_URL'] + 'projects/' + str(tracker_project_id) + '/stories', data=json.dumps(story), headers=post_header)

    return story_post.status_code


# change the story to finished if it was ever started, otherwise delete it
def close_story(tracker_project_id, story_id):
    put_header = dict({'Content-Type': 'application/json', 'X-TrackerToken': app.config['PTRACKER_API_KEY']})

    story_put = requests.put(app.config['PTRACKER_BASE_URL'] + 'projects/' + str(tracker_project_id) + '/stories/' + str(story_id),
                                data=json.dumps({'current_state': 'accepted'}), headers=put_header)
    status = story_put.status_code
    if status == 400:
        story_del = requests.delete(app.config['PTRACKER_BASE_URL'] + 'projects/' + str(tracker_project_id) + '/stories/' + str(story_id),
                                headers=put_header)
        status = story_del.status_code
    return status


def job_info():
    job_str = cStringIO.StringIO()
    scheduler.print_jobs(out=job_str)
    return job_str.getvalue()


