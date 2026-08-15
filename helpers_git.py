import subprocess
import helpers_slack

# GitHub-generated addresses that never resolve to a real Slack profile:
# noreply@github.com (bare merge/squash commits) and the privacy-enabled
# form <id>+<username>@users.noreply.github.com (bots, and any user with
# "Keep my email addresses private" turned on - this is common, not rare).
NOREPLY_DOMAIN_SUFFIX = '@users.noreply.github.com'
NOREPLY_BARE_ADDRESS = 'noreply@github.com'


def is_noreply_email(email):
    email = (email or '').strip().lower()
    return email == NOREPLY_BARE_ADDRESS or email.endswith(NOREPLY_DOMAIN_SUFFIX)


def resolve_git_ref_to_sha1(ref_name):
    print(f'Resolving {ref_name} to Git SHA1...')
    sha1 = subprocess.getoutput(f'git rev-parse {ref_name}')
    print(f'{ref_name} = {sha1}')
    return sha1


def get_commit_message_for_ref(ref_name, subject_only=True):
    print(f'Getting commit message for {ref_name}...')
    format = '%s' if subject_only else '%s\n%b'
    msg = subprocess.getoutput(f'git log -n1 --pretty=tformat:{format} {ref_name}')
    print(f'Message = {msg}')
    return msg


def get_author_email_for_ref(ref_name):
    print(f'Getting author email for {ref_name}...')
    email = subprocess.getoutput(f'git --no-pager show -s --format=%ae {ref_name}')
    print(f'Author email = {email}')
    return email


def get_committer_email_for_ref(ref_name):
    print(f'Getting committer email for {ref_name}...')
    email = subprocess.getoutput(f'git --no-pager show -s --format=%ce {ref_name}')
    print(f'Committer email = {email}')
    return email


def generate_diff(base_branch, current_commit_id, repo_url=''):
    remote_name = subprocess.getoutput('git remote')
    if remote_name == '':
        raise Exception(f'Can not get remote name. Out put of git remote command is: {remote_name}')
    base_sha1 = resolve_git_ref_to_sha1(f'{remote_name}/{base_branch}')
    diff = f'{base_sha1}..{current_commit_id}'

    # Add a list of commits that you are about to promote
    diff_info = f'Changes targeted for branch *{base_branch}*\n\n'
    if 'github' in repo_url or 'gitlab' in repo_url:
        diff_info += f'\nFull diff for changes to approve: {repo_url}/compare/{diff}\n\n'
    cmd = f'git log --pretty=format:"%h %<(27)%ai %<(20)%an  %s" --graph {diff}'
    diff_info += f'```{cmd}\n'
    diff_info += subprocess.getoutput(cmd)
    diff_info += '\n```'

    return helpers_slack.truncate_message_if_needed(
        diff_info,
        '\n\n diff info was truncated. Use link above to see full diff\n```\n\n')
