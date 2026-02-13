#!/bin/bash
# ChatBot Monitoring & Alerting Setup
# Sends alerts to adam.siehen@gmail.com
# Usage: sudo ./monitoring-alerts.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

ADMIN_EMAIL="adam.siehen@outlook.com"
HOSTNAME=$(hostname)

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check root
if [[ $EUID -ne 0 ]]; then
    echo "This script MUST be run as root"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Monitoring & Alerting Setup (Email: $ADMIN_EMAIL)       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# 1. Configure Postfix for Email Alerts
# ============================================
log_info "Configuring Postfix for email alerts..."

# Check if postfix is installed
if ! command -v postfix &> /dev/null; then
    apt install -y postfix mailutils
fi

# Configure postfix
cat > /etc/postfix/main.cf << EOF
# Postfix Configuration for ChatBot VPS

myhostname = $HOSTNAME
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mydestination = localhost

# TLS
smtp_use_tls = yes
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt

# Delivery
default_transport = smtp
relay_transport = smtp
local_transport = error
transport_maps = hash:/etc/postfix/transport

# Queue settings
maximal_queue_lifetime = 1d
bounce_queue_lifetime = 1d

# Local delivery
alias_maps = hash:/etc/aliases
EOF

# Create transport map for external SMTP (if needed)
cat > /etc/postfix/transport << EOF
# Local delivery only
localhost  smtp:[127.0.0.1]:25
EOF

postmap /etc/postfix/transport
systemctl restart postfix

log_success "Postfix configured"

# ============================================
# 2. Create Monitoring Scripts
# ============================================
log_info "Creating monitoring scripts..."

# Script: Check system health
mkdir -p /usr/local/lib/chatbot-monitors

cat > /usr/local/lib/chatbot-monitors/check-health.sh << 'EOF'
#!/bin/bash

HOSTNAME=$(hostname)
ADMIN_EMAIL="adam.siehen@gmail.com"
ALERT_SUBJECT="⚠️ [$HOSTNAME] Alert"

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    echo "Disk usage: ${DISK_USAGE}% (CRITICAL)"
    {
        echo "ALERT: Disk usage on $HOSTNAME is ${DISK_USAGE}%"
        echo ""
        echo "Disk status:"
        df -h
    } | mail -s "$ALERT_SUBJECT: Disk Critical" "$ADMIN_EMAIL"
fi

# Memory usage
MEM_USAGE=$(free | awk 'NR==2 {printf("%d", ($3/$2) * 100)}')
if [ "$MEM_USAGE" -gt 90 ]; then
    echo "Memory usage: ${MEM_USAGE}% (CRITICAL)"
    {
        echo "ALERT: Memory usage on $HOSTNAME is ${MEM_USAGE}%"
        echo ""
        echo "Memory status:"
        free -h
    } | mail -s "$ALERT_SUBJECT: Memory Critical" "$ADMIN_EMAIL"
fi

# Load average
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
CPUS=$(nproc)
LOAD_THRESHOLD=$(echo "$CPUS * 1.5" | bc)
if (( $(echo "$LOAD > $LOAD_THRESHOLD" | bc -l) )); then
    echo "Load average: $LOAD (threshold: $LOAD_THRESHOLD)"
    {
        echo "ALERT: High load average on $HOSTNAME: $LOAD"
        echo "CPU cores: $CPUS"
        echo ""
        echo "Process list:"
        ps aux --sort=-%cpu | head -10
    } | mail -s "$ALERT_SUBJECT: High Load" "$ADMIN_EMAIL"
fi

# Check Docker daemon
if ! docker ps &> /dev/null; then
    echo "Docker daemon not responding"
    {
        echo "ALERT: Docker daemon not responding on $HOSTNAME"
        echo ""
        echo "Docker status:"
        systemctl status docker
    } | mail -s "$ALERT_SUBJECT: Docker Down" "$ADMIN_EMAIL"
fi

# Check critical containers
for container in qdrant ollama node-red agent1_student; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "Container $container is not running"
        {
            echo "ALERT: Container $container is not running on $HOSTNAME"
            echo ""
            echo "Container status:"
            docker ps -a | grep "$container"
        } | mail -s "$ALERT_SUBJECT: Container Down" "$ADMIN_EMAIL"
    fi
done

# Check fail2ban bans
BAN_COUNT=$(fail2ban-client status | grep -oP '(?<=Jail list:).*' | wc -w)
if [ "$BAN_COUNT" -gt 5 ]; then
    echo "fail2ban active bans: $BAN_COUNT"
    {
        echo "ALERT: fail2ban has $BAN_COUNT active jails on $HOSTNAME"
        echo ""
        echo "fail2ban status:"
        fail2ban-client status
        echo ""
        echo "Recent bans (from auth.log):"
        grep "Ban" /var/log/fail2ban.log | tail -10
    } | mail -s "$ALERT_SUBJECT: Security Alert" "$ADMIN_EMAIL"
fi

exit 0
EOF

chmod +x /usr/local/lib/chatbot-monitors/check-health.sh

# Script: Monitor service restart events
cat > /usr/local/lib/chatbot-monitors/track-services.sh << 'EOF'
#!/bin/bash

HOSTNAME=$(hostname)
ADMIN_EMAIL="adam.siehen@gmail.com"

# Check if services were restarted
LAST_BOOT=$(systemctl show -p ActiveEnterTimestamp --value)
BOOT_TIME=$(date -d "$LAST_BOOT" +%s)
NOW=$(date +%s)
UPTIME_HOURS=$(( ($NOW - $BOOT_TIME) / 3600 ))

# If system rebooted in last 24 hours, send alert
if [ "$UPTIME_HOURS" -lt 24 ] && [ "$UPTIME_HOURS" -gt 0 ]; then
    {
        echo "NOTICE: System rebooted"
        echo ""
        echo "Uptime: $UPTIME_HOURS hours"
        echo "Last boot: $LAST_BOOT"
        echo ""
        echo "Service status:"
        systemctl status docker --no-pager
        systemctl status fail2ban --no-pager
    } | mail -s "NOTICE [$HOSTNAME] System Reboot" "$ADMIN_EMAIL"
fi

exit 0
EOF

chmod +x /usr/local/lib/chatbot-monitors/track-services.sh

log_success "Monitoring scripts created"

# ============================================
# 3. Create fail2ban alert integration
# ============================================
log_info "Integrating fail2ban alerts..."

cat > /etc/fail2ban/action.d/sendmail-alert.conf << 'EOF'
# Action: sendmail-alert
# Send email alert when IP is banned

[Definition]
actionstart = echo "Jail %(name)s started on <ip>" | mail -s "[fail2ban] %(name)s started" adam.siehen@gmail.com
actionstop = echo "Jail %(name)s stopped" | mail -s "[fail2ban] %(name)s stopped" adam.siehen@gmail.com
actioncheck = # placeholder
actionban = echo "IP banned: <ip>" | mail -s "[fail2ban] Ban alert from %(name)s" adam.siehen@gmail.com
actionunban = echo "IP unbanned: <ip>" | mail -s "[fail2ban] Unban alert from %(name)s" adam.siehen@gmail.com

[Init]
EOF

log_success "fail2ban alerts configured"

# ============================================
# 4. Create Cron Jobs for Monitoring
# ============================================
log_info "Creating monitoring cron jobs..."

# Health check every 4 hours
cat > /etc/cron.d/chatbot-health-check << 'EOF'
# Health monitoring for ChatBot VPS
0 */4 * * * root /usr/local/lib/chatbot-monitors/check-health.sh >> /var/log/chatbot-health-check.log 2>&1
EOF

# Service tracking daily
cat > /etc/cron.d/chatbot-service-tracking << 'EOF'
# Daily service status check
0 8 * * * root /usr/local/lib/chatbot-monitors/track-services.sh >> /var/log/chatbot-service-tracking.log 2>&1
EOF

# Security audit daily
cat > /etc/cron.d/chatbot-security-audit << 'EOF'
# Daily security audit
0 7 * * * root /usr/local/lib/chatbot-monitors/security-audit.sh >> /var/log/chatbot-security-audit.log 2>&1
EOF

log_success "Cron jobs created"

# ============================================
# 5. Create Security Audit Script
# ============================================
cat > /usr/local/lib/chatbot-monitors/security-audit.sh << 'EOF'
#!/bin/bash

HOSTNAME=$(hostname)
ADMIN_EMAIL="adam.siehen@gmail.com"

# Check SSH key access
UNAUTHORIZED_KEYS=$(grep -c "^ssh-rsa\|^ecdsa\|^ssh-ed25519" ~/.ssh/authorized_keys 2>/dev/null || echo 0)

# Get fail2ban stats
SSHD_BANS=$(fail2ban-client status sshd 2>/dev/null | grep -oP '(?<=Currently banned:).*' || echo "Unknown")

# Generate daily security report
{
    echo "=== Daily Security Report for $HOSTNAME ==="
    echo "Date: $(date)"
    echo ""
    echo "=== SSH Access ==="
    echo "Authorized keys: $UNAUTHORIZED_KEYS"
    echo ""
    echo "=== Firewall Status ==="
    ufw status
    echo ""
    echo "=== fail2ban Status ==="
    fail2ban-client status
    echo ""
    echo "=== Recent SSH Attempts ==="
    tail -20 /var/log/auth.log | grep "sshd\|ssh"
    echo ""
    echo "=== Open Ports ==="
    netstat -tulpn 2>/dev/null | grep LISTEN || ss -tulpn | grep LISTEN
    echo ""
} | mail -s "[Security] Daily Report - $HOSTNAME" "$ADMIN_EMAIL"

exit 0
EOF

chmod +x /usr/local/lib/chatbot-monitors/security-audit.sh

# ============================================
# 6. Send Test Email
# ============================================
log_info "Sending test email to $ADMIN_EMAIL..."

{
    echo "Test alert from ChatBot VPS"
    echo ""
    echo "Hostname: $HOSTNAME"
    echo "Time: $(date)"
    echo "Uptime: $(uptime)"
    echo ""
    echo "If you receive this email, alerting is working correctly."
} | mail -s "TEST: ChatBot VPS Monitoring Active" "$ADMIN_EMAIL"

log_success "Test email sent"

# ============================================
# 7. Create Monitoring Dashboard Script
# ============================================
cat > /usr/local/bin/chatbot-status << 'EOF'
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ChatBot VPS - Monitoring Dashboard               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "=== System Health ==="
echo "Uptime: $(uptime | awk -F'up' '{print $2}' | awk -F',' '{print $1}' | xargs)"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
echo "Memory Usage: $(free | awk 'NR==2 {printf("%.1f%%\n", ($3/$2)*100)}')"
echo ""

echo "=== Docker Services ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^NAMES|qdrant|ollama|agent|node-red"
echo ""

echo "=== Security Status ==="
echo "Firewall: $(ufw status | head -1)"
echo "fail2ban: $(systemctl is-active fail2ban)"
FAILED_SSH=$(grep -c "Failed password\|Invalid user" /var/log/auth.log 2>/dev/null | tail -100) 2>/dev/null || echo "0"
echo "SSH attempts (last 100): $FAILED_SSH"
echo ""

echo "=== Network Connections ==="
echo "SSH connections: $(netstat -tnp 2>/dev/null | grep :2222 | wc -l)" || echo "SSH connections: N/A"
echo "API connections: $(netstat -tnp 2>/dev/null | grep :8001 | wc -l)" || echo "API connections: N/A"
echo ""

echo "=== Recent Logs ==="
echo "Last errors (auth log):"
tail -5 /var/log/auth.log | grep -i "error\|fail\|ban" || echo "  No errors"
EOF

chmod +x /usr/local/bin/chatbot-status

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Monitoring & Alerting Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Configuration:${NC}"
echo "  ✓ Email alerts: $ADMIN_EMAIL"
echo "  ✓ Health checks: Every 4 hours"
echo "  ✓ Security audit: Daily at 7 AM"
echo "  ✓ Service tracking: Daily at 8 AM"
echo "  ✓ fail2ban integration: Alert on ban/unban"
echo ""

echo -e "${BLUE}Commands:${NC}"
echo "  chatbot-status          - View monitoring dashboard"
echo "  /usr/local/lib/chatbot-monitors/check-health.sh    - Run health check now"
echo "  /usr/local/lib/chatbot-monitors/security-audit.sh  - Run security audit now"
echo ""

echo -e "${YELLOW}You should receive a test email at: $ADMIN_EMAIL${NC}"
echo ""
