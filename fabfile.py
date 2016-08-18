# coding=utf-8
__author__ = 'pochnsong@163.com'

"""
终端输入
fab deploy 部署（安装相关软件+同步代码，已包含包含sync）
fab sync 同步代码
"""


from fabric.api import *
import time
from fab.utils import *
from fab import apache
import os
import re
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

""" User Configuration """

env.user = 'song'
env.hosts = ['133.130.55.240']
""" End of User Configuration """

proj_name = os.path.basename(os.path.dirname(__file__))
proj_path = '/home/%s/proj' % env.user
site_port = 8080


# -------------------------------------------
@task
def get_current_site():
    """
    return ensite, dissite
    """
    for line in run("ls /etc/apache2/sites-enabled").split():
        if re.match('^%s' % proj_name, line):
            if line.strip() == '%s_a.conf' % proj_name:
                return 'a', 'b'
            else:
                return 'b', 'a'

    return 'b', 'a'


@task
def init_www():
    """
    更新www文件夹
    """
    _remote_proj_path_a = os.path.join(proj_path, 'a')
    _remote_proj_root_a = os.path.join(_remote_proj_path_a, proj_name)
    if not exists(_remote_proj_path_a):
        run('mkdir -p %s' % _remote_proj_path_a)

    _remote_proj_path_b = os.path.join(proj_path, 'b')
    _remote_proj_root_b = os.path.join(_remote_proj_path_b, proj_name)
    if not exists(_remote_proj_path_b):
        run('mkdir -p %s' % _remote_proj_path_b)

    # 删除旧的资源文件
    for x in ['/var/www/%s/a/static' % proj_name,
              '/var/www/%s/a/media' % proj_name,
              '/var/www/%s/b/static' % proj_name,
              '/var/www/%s/b/media' % proj_name,
              '/var/www/%s/db' % proj_name,
              ]:
        sudo('rm -rf %s' % x)

    # 更新资源目录
    # /home/user/proj/a 项目目录
    # /var/www/seal/static 链接到项目目录中
    # /var/www/seal/media

    sudo('mkdir -p /var/www/%s/a' % proj_name)
    sudo('mkdir -p /var/www/%s/b' % proj_name)
    sudo('mkdir -p /var/www/%s/db' % proj_name)

    if not exists('/var/www/%s/backup' % proj_name):
        sudo('mkdir -p /var/www/%s/backup' % proj_name)
    sudo('chmod 777 /var/www/%s/backup' % proj_name)

    sudo('ln -sfn %s/static /var/www/%s/a/static' % (_remote_proj_root_a, proj_name))
    sudo('ln -sfn %s/media /var/www/%s/a/media' % (_remote_proj_root_a, proj_name))
    sudo('ln -sfn %s/static /var/www/%s/b/static' % (_remote_proj_root_b, proj_name))
    sudo('ln -sfn %s/media /var/www/%s/b/media' % (_remote_proj_root_b, proj_name))


@task
def init_env():
    """ Initialize server environment """
    install_virtualenv()
    create_virtualenv(proj_name)
    init_www()


def upload(_remote_proj_path, ignore='.fabfileignore'):
    tf_local = tar1(os.path.dirname(__file__), ignore=ignore)
    tf_name = proj_name + '.tar.gz'
    with cd(_remote_proj_path):
        print("uploading the project...(just wait:P)", str(os.path.getsize(tf_local)/1024)+'KB')
        put(tf_local, tf_name)
        sudo('rm -rf %s' % proj_name)
        print("untar ...")
        run('tar --no-overwrite-dir -zxvf %s' % tf_name)
        print('remove tar')
        run('rm %s' % tf_name)

    os.remove(tf_local)


@task
def deploy2():
    ensite, dissite = get_current_site()
    ensite_conf = '%s_%s.conf' % (proj_name, dissite)
    dissite_conf = '%s_%s.conf' % (proj_name, ensite)
    _remote_proj_path = "/".join([proj_path, dissite])
    _remote_proj_root = "/".join([_remote_proj_path, proj_name])

    upload(_remote_proj_path)
    with virtualenv(_remote_proj_root, proj_name):
        run("pip install -r requirements.txt")
        run('python manage.py collectstatic --noinput')
        run('rm -rf static')
        run('mv prod/static static')
        sudo('chmod -R 777 db')
        sudo('chmod -R 777 media')

@task
def start():
    ensite, dissite = get_current_site()

    _remote_proj_path = "/".join([proj_path, dissite])
    _remote_proj_root = "/".join([_remote_proj_path, proj_name])

    with virtualenv(_remote_proj_root, proj_name):
        run('chmod +x start_server.sh')
        sudo('./start_server.sh')


@task
def spv_start():
    """ Start supervisor Stop supervisor Stop supervisor"""
    ensite, dissite = get_current_site()

    _remote_proj_path = "/".join([proj_path, dissite])
    _remote_proj_root = "/".join([_remote_proj_path, proj_name])
    with virtualenv(_remote_proj_root, proj_name):
        sudo('supervisord -c supervisord.conf')

@task
def spv_stop():
    """ Stop supervisor """
    ensite, dissite = get_current_site()

    _remote_proj_path = "/".join([proj_path, dissite])
    _remote_proj_root = "/".join([_remote_proj_path, proj_name])

    with virtualenv(_remote_proj_root, proj_name):
        sudo('supervisorctl -c supervisord.conf stop all', warn_only=True)
        sudo('supervisorctl -c supervisord.conf shutdown', warn_only=True)
