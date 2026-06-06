from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
def to_rows(data):
    result = data.copy()

    for col in result.columns:
        if pd.api.types.is_datetime64_any_dtype(result[col]):
            result[col] = result[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    result = result.astype(object).where(pd.notnull(result), None)

    return result.to_dict(orient="records")


def get_kpi(engine):
    query = """
    SELECT 'Liczba logów sieciowych' AS metric, CAST(COUNT(*) AS VARCHAR(100)) AS value
    FROM dbo.network_logs

    UNION ALL

    SELECT 'Liczba alertów', CAST(COUNT(*) AS VARCHAR(100))
    FROM dbo.alerts

    UNION ALL

    SELECT 'Liczba reguł detekcji', CAST(COUNT(*) AS VARCHAR(100))
    FROM dbo.rules

    UNION ALL

    SELECT 'Liczba sensorów', CAST(COUNT(*) AS VARCHAR(100))
    FROM dbo.sensors

    UNION ALL

    SELECT 'Liczba scenariuszy', CAST(COUNT(*) AS VARCHAR(100))
    FROM dbo.scenario_labels

    UNION ALL

    SELECT 'Unikalne src_ip w logach', CAST(COUNT(DISTINCT src_ip) AS VARCHAR(100))
    FROM dbo.network_logs

    UNION ALL

    SELECT 'Unikalne src_ip w alertach', CAST(COUNT(DISTINCT src_ip) AS VARCHAR(100))
    FROM dbo.alerts

    UNION ALL

    SELECT 'Początek zakresu logów', CONVERT(VARCHAR(100), MIN([timestamp]), 120)
    FROM dbo.network_logs

    UNION ALL

    SELECT 'Koniec zakresu logów', CONVERT(VARCHAR(100), MAX([timestamp]), 120)
    FROM dbo.network_logs

    UNION ALL

    SELECT 'Początek zakresu alertów', CONVERT(VARCHAR(100), MIN(created_at), 120)
    FROM dbo.alerts

    UNION ALL

    SELECT 'Koniec zakresu alertów', CONVERT(VARCHAR(100), MAX(created_at), 120)
    FROM dbo.alerts;
    """

    return pd.read_sql(query, engine)


def get_quality_checks(engine):
    query = """
    SELECT 'Alerty bez pasującej reguły' AS check_name, COUNT(*) AS rows_count
    FROM dbo.alerts a
    LEFT JOIN dbo.rules r
        ON a.rule_id = r.id
    WHERE r.id IS NULL

    UNION ALL

    SELECT 'Logi bez pasującego sensora', COUNT(*)
    FROM dbo.network_logs l
    LEFT JOIN dbo.sensors s
        ON l.sensor_id = s.id
    WHERE s.id IS NULL

    UNION ALL

    SELECT 'Alerty bez pasującego sensora', COUNT(*)
    FROM dbo.alerts a
    LEFT JOIN dbo.sensors s
        ON a.sensor_id = s.name
    WHERE s.id IS NULL;
    """

    return pd.read_sql(query, engine)


def get_logs_alerts_time(engine):
    query = """
    WITH logs_by_hour AS (
        SELECT
            DATEADD(HOUR, DATEDIFF(HOUR, 0, [timestamp]), 0) AS event_hour,
            COUNT(*) AS logs_count
        FROM dbo.network_logs
        GROUP BY DATEADD(HOUR, DATEDIFF(HOUR, 0, [timestamp]), 0)
    ),

    alerts_by_hour AS (
        SELECT
            DATEADD(HOUR, DATEDIFF(HOUR, 0, created_at), 0) AS event_hour,
            COUNT(*) AS alerts_count
        FROM dbo.alerts
        GROUP BY DATEADD(HOUR, DATEDIFF(HOUR, 0, created_at), 0)
    )

    SELECT
        COALESCE(l.event_hour, a.event_hour) AS event_hour,
        ISNULL(l.logs_count, 0) AS logs_count,
        ISNULL(a.alerts_count, 0) AS alerts_count
    FROM logs_by_hour l
    FULL OUTER JOIN alerts_by_hour a
        ON l.event_hour = a.event_hour
    ORDER BY event_hour;
    """

    return pd.read_sql(query, engine)


def get_severity(engine):
    query = """
    SELECT
        severity,
        COUNT(*) AS alerts_count
    FROM dbo.alerts
    GROUP BY severity
    ORDER BY
        CASE severity
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
            WHEN 'info' THEN 5
            ELSE 6
        END;
    """

    return pd.read_sql(query, engine)


def get_top_suspicious_ips(engine):
    query = """
    SELECT
        src_ip,
        COUNT(*) AS alerts_count,
        SUM([count]) AS hits_count,
        SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) AS critical_alerts,
        SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) AS high_alerts,
        COUNT(DISTINCT rule_name) AS rules_count,
        MIN(created_at) AS first_seen,
        MAX(last_seen) AS last_seen
    FROM dbo.alerts
    GROUP BY src_ip
    ORDER BY
        critical_alerts DESC,
        alerts_count DESC,
        hits_count DESC;
    """

    result = pd.read_sql(query, engine)

    result["risk_score"] = (
        result["critical_alerts"] * 3
        + result["high_alerts"] * 2
        + result["hits_count"] * 0.2
        + result["rules_count"]
    ).round(1)

    result = result.sort_values(
        by=["risk_score", "alerts_count", "hits_count"],
        ascending=False
    )

    return result


def get_rules_summary(engine):
    query = """
    SELECT
        rule_name,
        severity,
        COUNT(*) AS alerts_count,
        SUM([count]) AS hits_count,
        COUNT(DISTINCT src_ip) AS src_ip_count,
        MIN(created_at) AS first_seen,
        MAX(last_seen) AS last_seen
    FROM dbo.alerts
    GROUP BY rule_name, severity
    ORDER BY hits_count DESC, alerts_count DESC;
    """

    return pd.read_sql(query, engine)


def get_scenario_summary(engine):
    query = """
    WITH log_scenarios AS (
        SELECT
            l.id,
            l.[timestamp],
            l.src_ip,
            l.dst_ip,
            l.dst_port,
            l.protocol,
            l.payload_size,
            COALESCE(sl.scenario, 'unlabeled') AS scenario
        FROM dbo.network_logs l
        LEFT JOIN dbo.scenario_labels sl
            ON l.[timestamp] BETWEEN sl.starts_at AND sl.ends_at
            AND (
                sl.src_ip = l.src_ip
                OR sl.src_ip LIKE '%' + l.src_ip + '%'
            )
    ),

    alert_scenarios AS (
        SELECT
            COALESCE(sl.scenario, 'unlabeled') AS scenario,
            COUNT(*) AS alerts_count
        FROM dbo.alerts a
        LEFT JOIN dbo.scenario_labels sl
            ON a.created_at BETWEEN sl.starts_at AND sl.ends_at
            AND (
                sl.src_ip = a.src_ip
                OR sl.src_ip LIKE '%' + a.src_ip + '%'
            )
        GROUP BY COALESCE(sl.scenario, 'unlabeled')
    )

    SELECT
        l.scenario,
        COUNT(*) AS logs_count,
        COUNT(DISTINCT l.src_ip) AS src_ip_count,
        COUNT(DISTINCT l.dst_ip) AS dst_ip_count,
        COUNT(DISTINCT l.dst_port) AS dst_port_count,
        AVG(CAST(l.payload_size AS FLOAT)) AS avg_payload_size,
        ISNULL(MAX(a.alerts_count), 0) AS alerts_count
    FROM log_scenarios l
    LEFT JOIN alert_scenarios a
        ON l.scenario = a.scenario
    GROUP BY l.scenario
    ORDER BY
        CASE WHEN l.scenario = 'normal' THEN 1 ELSE 0 END,
        alerts_count DESC,
        logs_count DESC;
    """

    return pd.read_sql(query, engine)


def get_anomaly_hours(time_data):
    result = time_data.copy()

    result["logs_mean"] = result["logs_count"].mean()
    result["logs_std"] = result["logs_count"].std()

    result["z_score"] = (
        (result["logs_count"] - result["logs_mean"]) / result["logs_std"]
    ).round(2)

    result = result[result["z_score"] >= 2].copy()

    result = result[
        ["event_hour", "logs_count", "alerts_count", "z_score"]
    ].sort_values("z_score", ascending=False)

    return result


def get_alert_hours(time_data):
    result = time_data[time_data["alerts_count"] > 0].copy()

    result = result[
        ["event_hour", "logs_count", "alerts_count"]
    ].sort_values("alerts_count", ascending=False)

    return result


def get_report_data(engine):
    time_data = get_logs_alerts_time(engine)

    result = {
        "kpi": get_kpi(engine),
        "quality": get_quality_checks(engine),
        "time_data": time_data,
        "severity": get_severity(engine),
        "top_ip": get_top_suspicious_ips(engine),
        "rules_summary": get_rules_summary(engine),
        "scenario_summary": get_scenario_summary(engine),
        "anomaly_hours": get_anomaly_hours(time_data),
        "alert_hours": get_alert_hours(time_data),
    }

    return result


def get_report_json(engine):
    data = get_report_data(engine)

    result = {}

    for name, table in data.items():
        result[name] = to_rows(table)

    return result


def export_report_tables(data, table_path):
    table_path.mkdir(parents=True, exist_ok=True)

    data["kpi"].to_csv(
        table_path / "kpi_report.csv",
        index=False,
        encoding="utf-8-sig"
    )

    data["top_ip"].head(10).to_csv(
        table_path / "top_suspicious_ips.csv",
        index=False,
        encoding="utf-8-sig"
    )

    data["rules_summary"].to_csv(
        table_path / "rules_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    data["scenario_summary"].to_csv(
        table_path / "scenario_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    data["anomaly_hours"].to_csv(
        table_path / "anomaly_hours.csv",
        index=False,
        encoding="utf-8-sig"
    )

    data["alert_hours"].to_csv(
        table_path / "alert_hours.csv",
        index=False,
        encoding="utf-8-sig"
    )

def save_chart(chart_path, name):
    chart_path = Path(chart_path)
    chart_path.mkdir(parents=True, exist_ok=True)

    png_path = chart_path / f"{name}.png"
    svg_path = chart_path / f"{name}.svg"

    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.savefig(svg_path)
    plt.close()

    return {
        "png": str(png_path),
        "svg": str(svg_path),
    }


def export_logs_alerts_time_chart(data, chart_path):
    time_data = data["time_data"]

    plt.figure(figsize=(12, 5))

    plt.plot(time_data["event_hour"], time_data["logs_count"], label="Logi sieciowe")
    plt.plot(time_data["event_hour"], time_data["alerts_count"], label="Alerty")

    plt.title("Liczba logów i alertów w czasie")
    plt.xlabel("Czas")
    plt.ylabel("Liczba zdarzeń")
    plt.legend()
    plt.xticks(rotation=45)

    return save_chart(chart_path, "logs_alerts_time")


def export_alerts_severity_chart(data, chart_path):
    severity = data["severity"]

    plt.figure(figsize=(8, 5))

    plt.bar(severity["severity"], severity["alerts_count"])

    plt.title("Rozkład alertów po severity")
    plt.xlabel("Severity")
    plt.ylabel("Liczba alertów")

    return save_chart(chart_path, "alerts_severity")


def export_top_suspicious_ips_chart(data, chart_path):
    ip_alerts = data["top_ip"]
    top_ip = ip_alerts.head(10).sort_values("risk_score")

    plt.figure(figsize=(10, 5))

    plt.barh(top_ip["src_ip"], top_ip["risk_score"])

    plt.title("Najbardziej podejrzane źródła IP")
    plt.xlabel("Risk score")
    plt.ylabel("src_ip")

    return save_chart(chart_path, "top_suspicious_ips")


def export_rules_hits_count_chart(data, chart_path):
    rules_summary = data["rules_summary"]
    rules_plot = rules_summary.sort_values("hits_count")

    plt.figure(figsize=(10, 5))

    plt.barh(rules_plot["rule_name"], rules_plot["hits_count"])

    plt.title("Reguły detekcji według liczby trafień")
    plt.xlabel("Suma trafień count")
    plt.ylabel("Reguła detekcji")

    return save_chart(chart_path, "rules_hits_count")


def export_rules_alerts_count_chart(data, chart_path):
    rules_summary = data["rules_summary"]
    rules_plot = rules_summary.sort_values("alerts_count")

    plt.figure(figsize=(10, 5))

    plt.barh(rules_plot["rule_name"], rules_plot["alerts_count"])

    plt.title("Reguły detekcji według liczby alertów")
    plt.xlabel("Liczba alertów")
    plt.ylabel("Reguła detekcji")

    return save_chart(chart_path, "rules_alerts_count")


def export_scenario_logs_count_chart(data, chart_path):
    scenario_summary = data["scenario_summary"]
    plot_data = scenario_summary.sort_values("logs_count")

    plt.figure(figsize=(10, 5))

    plt.barh(plot_data["scenario"], plot_data["logs_count"])

    plt.title("Liczba logów według scenariusza")
    plt.xlabel("Liczba logów")
    plt.ylabel("Scenariusz")

    return save_chart(chart_path, "scenario_logs_count")


def export_scenario_alerts_count_chart(data, chart_path):
    scenario_summary = data["scenario_summary"]
    plot_data = scenario_summary.sort_values("alerts_count")

    plt.figure(figsize=(10, 5))

    plt.barh(plot_data["scenario"], plot_data["alerts_count"])

    plt.title("Liczba alertów według scenariusza")
    plt.xlabel("Liczba alertów")
    plt.ylabel("Scenariusz")

    return save_chart(chart_path, "scenario_alerts_count")


def export_logs_anomalies_chart(data, chart_path):
    time_data = data["time_data"]
    anomaly_hours = data["anomaly_hours"]

    plt.figure(figsize=(12, 5))

    plt.plot(time_data["event_hour"], time_data["logs_count"], label="Logi sieciowe")

    plt.scatter(
        anomaly_hours["event_hour"],
        anomaly_hours["logs_count"],
        label="Potencjalne anomalie"
    )

    plt.title("Piki liczby logów w czasie")
    plt.xlabel("Czas")
    plt.ylabel("Liczba logów")
    plt.legend()
    plt.xticks(rotation=45)

    return save_chart(chart_path, "logs_anomalies")


def export_alert_hours_chart(data, chart_path):
    alert_hours = data["alert_hours"]

    plt.figure(figsize=(12, 5))

    plt.bar(alert_hours["event_hour"], alert_hours["alerts_count"], width=0.03)

    plt.title("Godziny z alertami")
    plt.xlabel("Czas")
    plt.ylabel("Liczba alertów")
    plt.xticks(rotation=45)

    return save_chart(chart_path, "alert_hours")


def export_report_charts(data, chart_path):
    result = {
        "logs_alerts_time": export_logs_alerts_time_chart(data, chart_path),
        "alerts_severity": export_alerts_severity_chart(data, chart_path),
        "top_suspicious_ips": export_top_suspicious_ips_chart(data, chart_path),
        "rules_hits_count": export_rules_hits_count_chart(data, chart_path),
        "rules_alerts_count": export_rules_alerts_count_chart(data, chart_path),
        "scenario_logs_count": export_scenario_logs_count_chart(data, chart_path),
        "scenario_alerts_count": export_scenario_alerts_count_chart(data, chart_path),
        "logs_anomalies": export_logs_anomalies_chart(data, chart_path),
        "alert_hours": export_alert_hours_chart(data, chart_path),
    }

    return result