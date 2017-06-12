#!/bin/bash

if [ -f ".env" ]
then
    export $(cat .env | grep -v ^# | xargs)
else
    echo "No .env file"
    exit 1
fi

adduser --disabled-password --uid 4801 --gecos "" ${USER_NAME}
adduser ${USER_NAME} sudo
#usermod --password $(echo $PASSWORD | openssl passwd -1 -stdin) ${USER_NAME}
echo "canary ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/90-cloudimg-ubuntu

# SSH acces setup
mkdir -p /home/${USER_NAME}/.ssh
chmod 700 /home/${USER_NAME}/.ssh

cp /root/.ssh/authorized_keys /home/${USER_NAME}/.ssh/
ssh-keygen -q -t rsa -b 2048 -N '' -f /home/${USER_NAME}/.ssh/id_rsa
sed -i  s/root/${USER_NAME}/g /home/${USER_NAME}/.ssh/id_rsa.pub
chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.ssh/

# TODO: Make optional
sed -i 's/#\?Port .\+/Port 8622/g' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin yes/PermitRootLogin no/g' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config
sed -i 's/^#\?AuthorizedKeysFile/AuthorizedKeysFile/g'  /etc/ssh/sshd_config
sed -i 's/^#\?X11Forwarding yes/X11Forwarding no/g'  /etc/ssh/sshd_config

service ssh restart

PUB_KEY=$(cat /home/${USER_NAME}/.ssh/id_rsa.pub)
curl -X POST --data-urlencode 'payload={"text": "'"${PUB_KEY}"'"}' ${SLACK_URL}

# TODO: Also check/install docker
REPO="deb https://apt.dockerproject.org/repo ubuntu-xenial main"
echo ${REPO} | tee /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-engine
service docker start
systemctl enable docker

curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# usermod -aG docker $USER  # Why does this not work?
groupadd docker
adduser ${USER_NAME} docker
service docker restart

apt-get update -y
apt-get install -y htop tree vim git jq mosh tmux curl rsync

mkdir -p /srv/apps/default
mkdir -p /srv/nginx/templates
curl -o /srv/nginx/templates/nginx.tmpl https://raw.githubusercontent.com/jwilder/nginx-proxy/master/nginx.tmpl
cp docker-compose.yml /srv/nginx/docker-compose.yml
chown -R ${USER_NAME}:${USER_NAME} /srv/

git clone https://github.com/obitec/wheel-factory.git /srv/build

passwd -l root

HOST_NAME=$(hostname)
IP=$(curl http://httpbin.org/ip | jq .origin | sed s/\"//g)

curl -X POST --data-urlencode \
  'payload={"username": "'"${USER_NAME}@${HOST_NAME}"'", "text": "Ready to serve... My IP is: '"${IP}"'"}' ${SLACK_URL}

rm -rf .env
rm -rf setup.sh

cd /srv/nginx && docker-compose up -d

# TODO Get more sustainable way to get chat_id. Maybe make it variable?
chat_id=$(curl -sS -X POST ${TELEGRAM_URL}/getUpdates | jq .result[0].message.chat.id)
curl -sS -X POST ${TELEGRAM_URL}/sendMessage -d text="Hello, World! I'm ${USER_NAME}@${HOST_NAME}, living at ${IP}" -d chat_id=${chat_id} | jq .
curl -sS -X POST ${TELEGRAM_URL}/sendMessage -d text="Here's my public key:\n${PUB_KEY}" -d chat_id=${chat_id} | jq .
curl -sS -X POST ${TELEGRAM_URL}/sendMessage -d text="Send me your's and I'll authorize access." -d chat_id=${chat_id} | jq .

history -c && history -w
