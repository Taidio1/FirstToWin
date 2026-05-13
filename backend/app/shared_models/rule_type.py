import enum


class RuleType(str, enum.Enum):
    blacklist_ip = "blacklist_ip"
    connection_threshold = "connection_threshold"
    port_scan = "port_scan"
    protocol_filter = "protocol_filter"
