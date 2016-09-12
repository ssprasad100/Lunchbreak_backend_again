import getpass
import os

from fabric.api import env, local, run, sudo
from fabric.context_managers import cd, hide, quiet, settings
from fabric.operations import put

# Host
HOST = '46.101.96.234'
#HOST = os.environ.get('LUNCHBREAK_HOST', input('Host: '))

# Fabric environment
env.hosts = [HOST]
env.user = 'root'
env.shell = '/bin/bash -c -l'

# Git information
with hide('running', 'output'):
    with settings(warn_only=True), hide('warnings'):
        git_tag = os.environ.get(
            'TRAVIS_TAG',
            local(
                'git describe --exact-match --tags $(git log -n1 --pretty=\'%h\')',
                capture=True
            )
        )
    git_commit = os.environ.get(
        'TRAVIS_COMMIT',
        local('git rev-parse --verify HEAD', capture=True)
    )
    git_branch = os.environ.get(
        'TRAVIS_BRANCH',
        local('git rev-parse --abbrev-ref HEAD', capture=True)
    )
    git_branch = 'staging' if git_branch not in ['master', 'staging'] else git_branch

if git_tag:
    print('Current git tag: ' + str(git_tag))
else:
    print('No current git tag.')
print('Current git commit: ' + str(git_commit))
print('Current git branch: ' + str(git_branch))

is_production = git_tag and git_branch == 'master'
if is_production:
    print('We\'re currently on production!')


def deploy(username=None, password=None):
    """The regular deployment.

    Tests, pushes new image and updates server."""
    local('tox')
    push(
        username=username,
        password=password
    )
    deployer = Deployer()
    deployer.update_server()


def push(username=None, password=None):
    """Only builds and pushes new image."""
    deployer = Deployer(
        username=username,
        password=password
    )
    deployer.push_images()


def upload_compose_config():
    """Upload new docker-compose configs."""
    deployer = Deployer()
    deployer.update_compose_config()


def setup():
    """Setup the server."""
    deployer = Deployer()
    deployer.setup()


class Deployer:

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def push_images(self):
        """Build and push the image with the associated tags."""
        self._docker_login(remote=False)

        # Create all tags associated with this image
        docker_tags = [
            # Each commit will have a history in the registry
            git_commit,
            # Tagged commits are meant for production
            'production' if is_production else 'latest'
        ]
        # Each tag will have a history in the registry
        if git_tag:
            docker_tags.append(git_tag)

        # Generate all the image names from the tags
        image_names = []
        for tag in docker_tags:
            image_name = self._image_name(
                tag=tag
            )
            image_names.append(image_name)

        build_args = {
            'version': 'production' if is_production else 'staging',
            'certificate_type': 'production' if is_production else 'development'
        }

        # Build the image and tag it with all of the names
        local(
            'docker build -t {image_names} --build-arg {build_args} .'.format(
                image_names=' -t '.join(image_names),
                build_args=' --build-arg '.join(
                    ['%s=%s' % (key, value) for key, value in build_args.items()]
                )
            )
        )

        # Push all associated tags
        for image_name in image_names:
            local(
                'docker push {image_name}'.format(
                    image_name=image_name
                )
            )

    def update_server(self):
        """Make sure the remote server updates its containers."""
        with hide('output'):
            sudo('apt-get update')
            sudo('apt-get upgrade')

            self._setup_ufw()

        # Ensure Fail2ban is running
        # sudo('fail2ban-client reload')
        # sudo('fail2ban-client start')

        self._compose_up(
            service='lunchbreak_' + str('staging' if not is_production else 'production')
        )

    def update_compose_config(self, configs=None):
        self._compose_up(
            configs=configs
        )

    def setup(self, **kwargs):
        """Install all of the required software.

        Only works on Ubuntu 16.04 LTS.
        """

        # Docker installation
        with hide('output'):
            sudo('apt-get update')
            sudo('apt-get upgrade -y')
            sudo('apt-get install apt-transport-https ca-certificates -y')
            sudo('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
            sudo('echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" > /etc/apt/sources.list.d/docker.list')

            sudo('apt-get update')
            sudo('apt-get purge lxc-docker')
            sudo('apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual -y')
            sudo('apt-get install docker-engine -y')

            sudo('service docker start')
            sudo('systemctl enable docker')

            # Docker compose installation
            sudo('apt-get install python-pip')
            sudo('pip install --no-input docker-compose')

            self._setup_ufw()

        sudo('mkdir /etc/lunchbreak/docker -p')
        put(
            local_path='docker',
            remote_path='/etc/lunchbreak'
        )
        self.update_compose_config(**kwargs)

    def _image_name(self, tag):
        return '{username}/lunchbreak:{tag}'.format(
            username=self.username,
            tag=tag
        )

    def _setup_ufw(self):
        """Firewall settings."""
        sudo('ufw default deny incoming')
        sudo('ufw default allow outgoing')
        sudo('ufw allow ssh')
        sudo('ufw allow http')
        sudo('ufw allow https')
        sudo('ufw --force enable')
        sudo('ufw --force reload')

    def _docker_login(self, remote=True):
        if not self.username:
            self.username = self.username \
                if self.username is not None \
                else os.environ.get('DOCKER_USERNAME', input('Docker Hub username: '))
        if not self.password:
            self.password = self.password \
                if self.password is not None \
                else os.environ.get('DOCKER_PASSWORD', getpass.getpass('Docker Hub password: '))

        with quiet():
            method = local if not remote else sudo
            method(
                'docker login -u="{username}" -p="{password}"'.format(
                    username=self.username,
                    password=self.password
                )
            )

    def _compose_up(self, configs=None, service=None):
        """Update docker compose containers.

        Will restart all container if no service is given.
        Else it will only restart that specific service.

        Args:
            configs (:obj:`string`): Configs that need to be used, will be uploaded if found.
            service (:obj:`string`, optional): Specific service that needs to be restarted.
        """
        if configs is None:
            configs = [
                './docker/docker-compose.yml',
                './docker/docker-compose.production.yml'
            ]

        with cd('/etc/lunchbreak'):
            if configs is not None:
                for config in configs:
                    if os.path.isfile(config):
                        put(
                            local_path=config,
                            remote_path='/etc/lunchbreak'
                        )

            self._docker_login()
            run('docker-compose pull')

            config_params = '-f ' + ' -f '.join(
                [os.path.basename(config) for config in configs]
            )

            if service is not None:
                run(
                    'docker-compose {config_params} up --no-deps -d {service}'.format(
                        service=service,
                        config_params=config_params
                    )
                )
            else:
                run('docker-compose down')
                run(
                    'docker-compose {config_params} up -d'.format(
                        config_params=config_params
                    )
                )
