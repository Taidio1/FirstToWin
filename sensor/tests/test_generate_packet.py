import os
import sys
import pytest

os.environ.setdefault("SENSOR_NAME", "test-sensor")
os.environ.setdefault("SENSOR_KEY", "test-key")
os.environ.setdefault("SENSOR_MODE", "mixed")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sensor import generate_packet

REQUIRED_FIELDS = {"sensor_name", "src_ip", "dst_ip", "src_port", "dst_port", "protocol", "flags", "payload_size"}


def test_port_scan_has_required_fields():
    packet = generate_packet("port-scan")
    assert REQUIRED_FIELDS.issubset(packet.keys())


def test_port_scan_uses_consistent_src_ip():
    packets = [generate_packet("port-scan") for _ in range(10)]
    src_ips = {p["src_ip"] for p in packets}
    assert len(src_ips) == 1, "port-scan must use one src_ip to trigger detection"


def test_port_scan_cycles_distinct_ports():
    packets = [generate_packet("port-scan") for _ in range(5)]
    ports = [p["dst_port"] for p in packets]
    assert len(set(ports)) == 5, "port-scan must emit 5 distinct dst_ports to trigger alert"


def test_ssh_bruteforce_always_port_22():
    for _ in range(20):
        packet = generate_packet("ssh-bruteforce")
        assert packet["dst_port"] == 22


def test_ssh_bruteforce_consistent_src_ip():
    packets = [generate_packet("ssh-bruteforce") for _ in range(10)]
    src_ips = {p["src_ip"] for p in packets}
    assert len(src_ips) == 1, "ssh-bruteforce must use one src_ip to trigger detection"


def test_mixed_returns_valid_packet():
    for _ in range(30):
        packet = generate_packet("mixed")
        assert REQUIRED_FIELDS.issubset(packet.keys())


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="Unknown SENSOR_MODE"):
        generate_packet("invalid-mode")
