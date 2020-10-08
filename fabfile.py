import datetime
from fabric.api import cd, env, task, run, prefix
from fabric.contrib.project import rsync_project
from fabric.utils import puts
from contextlib import contextmanager

env.use_ssh_config = True
env.activate = 'source venv/bin/activate'

STAGES = {
    'production': {
        'hosts': ['51.81.47.208'],
        'code_dir': '/home/ubuntu/yas',
        'code_branch': 'master',
    },
    'test': {
        'hosts': ['yastest.crescente.com.ar'],
        'code_dir': '/home/juan/yas',
        'code_branch': 'master',
    }
}


def stage_set(stage_name='test'):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)


@task
def production():
    stage_set('production')
    env.user = 'ubuntu'
    env.group = ':www-data'


@task
def test():
    stage_set('test')
    env.user = 'root'
    env.group = 'juan:www-data'

@task
def makemigrations():
    """
    Make migrations! CAUTION! DO NOT USE IT IN PRODUCTION
    """
    with cd(env.code_dir):
        run('python manage.py makemigrations')


@task
def migrate():
    """
    Migrate the database to the latest version.
    """
    with cd(env.code_dir):
        run('python manage.py migrate')


@task
def collect_static():
    """
    Migrate the database to the latest version.
    """
    with cd(env.code_dir):
        run('python manage.py collectstatic --noinput -v 0')


@task
def pip_install():
    """
    Install the pip requirements
    """
    with cd(env.code_dir):
        run('pip3 install -r requirements.txt')


@task
def npm_i():
    """
    Install the npm dependecies for production.
    """
    with cd(env.code_dir):
        run('npm i')

@task
def npm_build():
    """
    Build the js compressed file for production.
    """
    with cd(env.code_dir):
        run('npm run build:prod')

@task
def bower_install():
    """
    Install the bower dependencies
    """
    with cd(env.code_dir):
        run('bower install --allow-root')


@task
def pull():
    """
    Pull from repo
    """
    with cd(env.code_dir):
        run('git pull origin %s' % (env.code_branch, ))


@task
def checkout_master():
    with cd(env.code_dir):
        run('git checkout %s' % (env.code_branch, ))


@task
def stash():
    with cd(env.code_dir):
        run('git stash')


@task
def restart_gunicorn():
    """
    Pull from repo
    """
    run('systemctl restart gunicorn')


@task
def restart_nginx():
    """
    Pull from repo
    """
    run('systemctl restart nginx')



@task
def restart_nginx():
    run('systemctl restart nginx')

@task
def restart_apache():
    """
    Pull from repo
    """
    run('systemctl restart apache2')

@task
def fix_static_permissions():
    """
    Fix static permissions
    """
    run('sudo chown -R {} static'.format(env.group))
    run('sudo chmod -R 770 static')

@task
def fix_media_permissions():
    """
    Fix media permissions
    """
    run('sudo chown -R {} media'.format(env.group))
    run('sudo chmod -R 770 media')
    

@task
def update():
    """
    fab test deploy
    fab production deploy
    """

    with cd(env.code_dir):
        with prefix("source venv/bin/activate"):
            run('python manage.py updates')
    puts("             DONE               ")

@task
def deploy():
    """
    fab test deploy
    fab production deploy
    """
    print("Executing on %(host)s as %(user)s" % env)
    with cd(env.code_dir):
        checkout_master()
        stash()
        pull()
        npm_i()
        npm_build()
        bower_install()
        with prefix("source venv/bin/activate"):
            pip_install()
            migrate()
            collect_static()
            restart_gunicorn()
        if env.stage == 'test':
            restart_apache()
        if env.stage == 'production':
            restart_nginx()
        fix_static_permissions()
        fix_media_permissions()
    puts("               |    |    |               ")
    puts("              )_)  )_)  )_)              ")
    puts("             )___))___))___)\            ")
    puts("            )____)____)_____)\\          ")
    puts("          _____|____|____|____\\\__      ")
    puts(" ---------\                   /--------- ")
    puts("   ^^^^^ ^^^^^^^^^^^^^^^^^^^^^           ")
    puts("     ^^^^      ^^^^     ^^^    ^^        ")
    puts("          ^^^^      ^^^                  ")
    puts("           ^^^       ^^^^^^              ")
