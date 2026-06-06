# Mock NDR Dataset

Generated mock data for the FirstToWin NDR project.

## Generation settings

- Days: 7
- Network logs: 5000
- Alerts: 36
- Seed: 20260527
- Timezone: UTC

## Files

- `network_logs.csv` - synthetic network events compatible with the `network_logs` table.
- `alerts.csv` - alerts derived from attack clusters.
- `rules.csv` - detection rules used for the alerts.
- `sensors.csv` - demo sensors without API keys or secrets.
- `scenario_labels.csv` - analyst-friendly labels mapping source IPs and time windows to scenarios.

## Suggested report angles

- Alert volume over time.
- Severity distribution.
- Top source IPs by alert count.
- Rule effectiveness based on hit counts.
- Normal traffic baseline compared with simulated attacks.
