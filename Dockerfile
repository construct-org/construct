From asciinema/asciinema


# Install pip

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y git

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install wheel


# Install construct

RUN pip install git+git://github.com/construct-org/construct_setup.git -I --process-dependency-links --trusted-host github.com
RUN pip install spielbash
RUN echo "source /usr/local/bin/construct.sh" >> /root/.bashrc
