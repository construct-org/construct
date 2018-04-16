FROM asciinema/asciicast2gif


# Install convert CMD

ADD convert.sh /root/convert.sh
RUN chmod +x /root/convert.sh


# Install font

RUN apt-get update
RUN apt-get -y install unifont
RUN fc-cache -f -v


# Add unifont to head of font-family for asciinema-player.css

RUN sed -i 's/font-family: C/font-family: unifont, C/g' /app/page/asciinema-player.css


ENTRYPOINT ["/root/convert.sh"]
