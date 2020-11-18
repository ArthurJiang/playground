FROM python:3.7

WORKDIR /playground

# Copy files
ADD requirements.txt requirements.txt
ADD run.sh run.sh

# Setup notebook
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN jupyter contrib nbextension install --system
RUN jt -t onedork -fs 95 -altp -tfs 11 -nfs 115 -cellw 88% -T


# Install redis
RUN wget http://download.redis.io/releases/redis-6.0.6.tar.gz; tar xzf redis-6.0.6.tar.gz; cd redis-6.0.6; make
RUN rm redis-6.0.6.tar.gz

# Install others
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update
RUN apt-get install -y zsh
RUN apt-get install -y htop
RUN apt-get install -y jq
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || echo hi
RUN chsh -s `which zsh` && wget https://raw.githubusercontent.com/ArthurJiang/config/master/.zshrc -O ~/.zshrc
RUN apt-get install -y npm
RUN rm -rf /var/lib/apt/lists/*
RUN npm install -g redis-commander

# Start service
CMD ["/bin/bash", "./run.sh"]