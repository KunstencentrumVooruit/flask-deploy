###############
### imports ###
###############

from fabric.api import cd, env, lcd, put, prompt, local, sudo, run
from fabric.contrib.files import exists, append
import os, sys


##############
### config ###
##############

local_app_dir = './flask_project'
local_config_dir = 'config'

remote_app_dir = '/home/flask/apps'
remote_git_dir = '/home/flask/git'
remote_flask_dir = remote_app_dir + '/flask_project'
remote_nginx_dir = '/etc/nginx/sites-enabled'
remote_supervisor_dir = '/etc/supervisor/conf.d'

env.hosts = ['192.168.2.41']  # replace with IP address or hostname
env.user = 'flask'
# env.password = 'blah!'


#############
### tasks ###
#############
def configure_nginx():
    """
    1. Remove default nginx config file
    2. Create new config file
    3. Setup new symbolic link
    4. Copy local config to remote config
    5. Restart nginx
    """
    sudo('/etc/init.d/nginx start')
    if exists('/etc/nginx/sites-enabled/default'):
        sudo('rm /etc/nginx/sites-enabled/default')
    if exists('/etc/nginx/sites-enabled/flask_project') is False:
        sudo('touch /etc/nginx/sites-available/flask_project')
        sudo('ln -s /etc/nginx/sites-available/flask_project' +
             ' /etc/nginx/sites-enabled/flask_project')
    with lcd(local_config_dir):
        with cd(remote_nginx_dir):
            put('./flask_project', './', use_sudo=True)
    sudo('/etc/init.d/nginx restart')


def configure_supervisor(file):
    """
    1. Create new supervisor config file
    2. Copy local config to remote config
    3. Register new command
    """
    if exists('/etc/supervisor/conf.d/' + file) is False:
        with lcd(local_config_dir):
            with cd(remote_supervisor_dir):
                put(file, './', use_sudo=True)
                sudo('supervisorctl reread')
                sudo('supervisorctl update')


def configure_git(appname):
    """
    1. Setup bare Git repo
    2. Create post-receive hook
    """
    if exists(remote_git_dir) is True:
        
        with cd(remote_git_dir):
            run('mkdir ' + appname + '.git')
            with cd(appname + '.git'):
                run('git init --bare')
                with lcd(local_config_dir):
                    with cd('hooks'):
                        put('post-receive', './')
                        append('./post-receive', "GIT_WORK_TREE=" + remote_app_dir + "/" + appname + " git checkout -f")
                        run('chmod +x post-receive')

def deployToServer(app):
    """
    1. Copy new Flask files
    2. Restart gunicorn via supervisor
    """
    with lcd('../' + app):
        local('git add -A')
        commit_message = prompt("Commit message?")
        local('git commit -am "{0}"'.format(commit_message))
        local('git push production master')
        #sudo('supervisorctl restart flask_project')


def rollback():
    """
    1. Quick rollback in case of error
    2. Restart gunicorn via supervisor
    """
    with lcd(local_app_dir):
        local('git revert master  --no-edit')
        local('git push production master')
        sudo('supervisorctl restart flask_project')


def status():
    """ Is our app live? """
    sudo('supervisorctl status')

def create():
    update()
    #local ('rm -Rf ../nam')
    appname = prompt('Enter directory name for new Flask app: ')
    print "Creating new virtualenv for " + appname
    with lcd('../'):
        local('virtualenv ' + appname)
    with lcd('../' + appname):
        print "***** Installing Flask, Flask-restplus, gunicorn ..."
        local('bin/pip install flask flask-restplus gunicorn')
        print "***** Making app.py from template ..."
        local('cp ../flask-deploy/template.py app.py')
        local('cp ../flask-deploy/config/.gitignore .')
        local('chmod 775 app.py')
        local('mkdir static')
            

def deploy():
    update()
    # 1. Controleer indien eerste deploy. Indien True:
    #       -> maak git repo aan op remote
    #       -> create flask directory 
    appname = prompt('Name of directory of app to deploy?')
    #if exists('../' + app) is True:
    #with lcd('../' + app):
    print "***** Checking if first deploy ..."
    if exists(remote_git_dir + '/' + appname + '.git') is False:
    	print "***** First deploy, doing stuff"
    	print "***** Configuring local git ..."
        with lcd('../' + appname):
        	local('git init')
        	local('git remote add production flask@192.168.2.41:' + remote_git_dir + '/' + appname + '.git')
        print "***** Configuring git on server"
        configure_git(appname)
        print "***** Creating app directory on server ..."
        with cd(remote_app_dir):
            run('git clone ' + remote_git_dir + '/' + appname + '.git')
    deployToServer(appname)
        
def update():
    m = local('git pull', capture=True)
    if m == "Already up-to-date.":
        print m
    else:
        print "***** Found update. Restarting!"
        os.execl('/usr/bin/fab', 'fab', sys.argv[1]) # 2Do: allow more arguments

def configSupervisor():
    app = prompt('Name of app to deploy?')
    port = prompt('Listening port? (500x)')
    local('echo [program:' + app + '] > config/' + app + '.conf')
    local ('echo command = gunicorn app:app -b localhost:' + port + ' >> config/' + app + '.conf')
    local ('echo directory = ' + remote_app_dir + '/' + app + ' >> config/' + app + '.conf')
    local ('echo user = flask >> config/' + app + '.conf')
    configure_supervisor(app + '.conf')
    
