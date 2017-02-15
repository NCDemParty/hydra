from awsfabrictasks.ec2.api import *
from fabric.api import *
from functools import wraps

import boto.ec2.elb
import boto.ec2.connection
import boto.ec2.instance
import time


def aws_hosts(load_balancers):
    instances = []
    elb_conn = boto.ec2.elb.connect_to_region('us-west-2', profile_name="hydra")
    for elb in elb_conn.get_all_load_balancers(load_balancer_names=load_balancers):
        instances.extend(elb.instances)

    if not instances:
      raise ValueError('No instances found! I\'m getting out of here.')

    ec2_conn = boto.ec2.connect_to_region('us-west-2', profile_name="hydra")
    reservations = ec2_conn.get_all_instances([i.id for i in instances])

    ec2_hosts = {}
    for reservation in reservations:
        for i in reservation.instances:
            ec2_hosts[i.public_dns_name] = i.id

    return ec2_hosts


def elb_operation(operation, instance_id, loadBalancerNames):
    elb_conn =  boto.ec2.elb.connect_to_region('us-west-2', profile_name="hydra")
    for lb in elb_conn.get_all_load_balancers(load_balancer_names=loadBalancerNames):
        getattr(lb, operation)(instance_id)


def remove_from_elbs():
    print "Removing %s from the load balancer..." % env.aws_hosts[env.host]
    elb_operation('deregister_instances', env.aws_hosts[env.host], env.load_balancer_name)
    time.sleep(5)    # allow connections to fully drain


def add_to_elbs():
    print "Adding %s back to the load balancer..." % env.aws_hosts[env.host]
    elb_operation('register_instances', env.aws_hosts[env.host], env.load_balancer_name)
    time.sleep(15)   # generous to prevent cascading effect of removing machines from ELB


def elb_managed(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        
        if env.load_balancer_name:
            remove_from_elbs()

        func(*args, **kwargs)
        
        if env.load_balancer_name:
            add_to_elbs()
            
    return decorated


def production():
    env.load_balancer_name = ["hydra"]
    env.aws_hosts = aws_hosts(env.load_balancer_name)
    env.hosts = env.aws_hosts.keys()
    env.forward_agent = True
    env.key_filename = '~/.ssh/hydra.pem'
    env.user = 'ubuntu'
    env.env_name = 'production'


def staging():
    env.load_balancer_name = None
    env.hosts = ['ec2-35-162-74-89.us-west-2.compute.amazonaws.com']
    env.forward_agent = True
    env.key_filename = '~/.ssh/hydra.pem'
    env.user = 'ubuntu'
    env.env_name = 'staging'


@elb_managed
def deploy(pip_install=False, migrate=False):

    with cd('hydra'):
        with prefix('source $(which virtualenvwrapper.sh)'):
            with prefix('workon hydra'):

                if env.env_name != 'staging':
                    run('supervisorctl stop gunicorn')

                run('git pull origin master')

                if env.env_name != 'staging':
                    run('./manage.py collectstatic --noinput')

                if str(pip_install).lower() == 'true':
                    run('pip install -r requirements.txt')

                if str(migrate).lower() == 'true':
                    run('./manage.py migrate --settings=hydra.settings_for_migrations')

                if env.env_name != 'staging':
                    run('supervisorctl start gunicorn')
                
                # todo: varnish?, etc.


@elb_managed
def restart_gunicorn():

    with cd('hydra'):
        with prefix('source $(which virtualenvwrapper.sh)'):
            with prefix('workon hydra'):
                run('supervisorctl restart gunicorn')

@elb_managed
def config_set(**kwargs):
    if not kwargs:
        print "kwargs empty! Pass in a variable you want to set"
        print "e.g.: fab production config_set:DOUBLE_SECRET_PASSWORD=\"yolo\""
        exit(1)

    # this is going to get untenable... use with discretion!
    with cd('/home/ubuntu/.virtualenvs/hydra/bin'):
        for key, value in kwargs.iteritems():
            run('echo "\nexport %s=%s" >> activate' % (key, value))

    with cd('hydra'):
        with prefix('source $(which virtualenvwrapper.sh)'):
            with prefix('workon hydra'):
                # manually stop gunicorn
                run('supervisorctl stop gunicorn')
                run('cat supervisord.pid | xargs kill')
                run('supervisord')
                run('supervisorctl reload')
                run('supervisorctl start gunicorn')