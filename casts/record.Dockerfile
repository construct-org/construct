From asciinema/asciinema


# Install pip

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y git
RUN apt-get install -y tmux

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install wheel


# Install construct

RUN pip install git+git://github.com/construct-org/construct_setup.git -I --process-dependency-links --trusted-host github.com
RUN echo "source /usr/local/bin/construct.sh" >> /root/.bashrc


# Install spielbash

RUN pip install git+git://github.com/danbradham/spielbash.git


# Configure tmux

ADD .tmux.conf /root/.tmux.conf


# Install record CMD

ADD record.sh /src/record.sh
RUN chmod +x /src/record.sh


# Setup data volume

WORKDIR /data
VOLUME ["/data"]


# Set PS1
RUN echo 'export PS1="\w> "' >> /root/.bashrc


ENTRYPOINT ["/src/record.sh"]
