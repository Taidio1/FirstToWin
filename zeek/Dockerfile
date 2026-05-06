  FROM zeek/zeek:6-lts

  COPY node.cfg /etc/zeek/node.cfg
  COPY local.zeek /etc/zeek/local.zeek

  CMD ["zeek", "-i", "vboxnet0", "/etc/zeek/local.zeek"]