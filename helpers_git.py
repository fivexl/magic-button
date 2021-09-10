import subprocess

def resolve_git_ref_to_sha1(ref_name):
    print(f'Resolving {ref_name} to Git SHA1...')
    sha1 = subprocess.getoutput(f'git rev-parse {ref_name}')
    print(f'{ref_name} = {sha1}')
    return sha1


def get_commit_message_for_ref(ref_name, subject_only=True):
    print(f'Getting commit message for {ref_name}...')
    format='%s' if subject_only else '%s\n%b'
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
    cmd = f'git log --pretty=format:"%h %<(27)%ai %<(20)%an  %s" --graph {diff}'
    diff_info = f'Change log for changes to approve:\n```\n{cmd}\n'
    diff_info += subprocess.getoutput(cmd)
    diff_info += '\n```\n\n'

    if 'github' in repo_url or 'gitlab' in repo_url:
        diff_info += f'\nFull diff for changes to approve: {repo_url}/compare/{diff}\n\n'

    return diff_info