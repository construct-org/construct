FROM asciinema/asciicast2gif


# Install convert CMD

ADD convert.sh /root/convert.sh
RUN chmod +x /root/convert.sh


ENTRYPOINT []
CMD ["./convert.sh"]
