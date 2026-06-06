 FROM jasonish/suricata:7

  RUN suricata-update update-sources && suricata-update

  COPY suricata.yaml /etc/suricata/suricata.yaml

  CMD ["suricata", "-i", "vboxnet0", "-c", "/etc/suricata/suricata.yaml"]