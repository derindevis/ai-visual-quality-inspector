from email_alerts import send_defect_alert, send_daily_summary

# Test defect alert
send_defect_alert(
    image_name     = "test_image.png",
    defect_type    = "MT_Crack",
    confidence     = 0.87,
    severity       = "HIGH 🔴",
    region         = "Upper-Left",
    recommendation = "REJECT — Immediately remove from production line"
)

# Test daily summary
send_daily_summary(
    total     = 173,
    passed    = 28,
    failed    = 145,
    pass_rate = 16.2
)