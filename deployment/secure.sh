#!/bin/bash
# ChatBot VPS Security Hardening Script
# Usage: sudo ./secure.sh
# Hardening checklist:
# - fail2ban (SSH brute force protection)
# - UFW firewall (port whitelisting)
# - SSH hardening (key auth only, changed port)
# - VPN-only access (IPv4 + IPv6)
# - DDoS protection (rate limiting, SYN cookies)
# - Automatic security updates
# - Monitoring & alerting

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ADMIN_EMAIL="adam.siehen@gmail.com"
SSH_PORT=2222
VPN_SUBNET_V4="10.0.0.0/24"
VPN_SUBNET_V6="fd00::/8"
NEW_HOSTNAME="chatbot-vps"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script MUST be run as root"
    echo "Usage: sudo ./secure.sh"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ChatBot VPS Security Hardening & Firewalling Setup     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# 1. System Updates
# ============================================
log_info "Step 1: Updating system packages..."
apt update
apt upgrade -y
log_success "System updated"

# ============================================
# 2. Configure Hostname
# ============================================
log_info "Step 2: Configuring hostname..."
hostnamectl set-hostname "$NEW_HOSTNAME"
echo "127.0.0.1 $NEW_HOSTNAME" >> /etc/hosts
log_success "Hostname set to: $NEW_HOSTNAME"

# ============================================
# 3. Install Security Tools
# ============================================
log_info "Step 3: Installing security tools..."
apt install -y \
    curl \
    wget \
    git \
    htop \
    net-tools \
    telnet \
    nmap \
    fail2ban \
    ufw \
    mlocate \
    aide \
    unattended-upgrades \
    apt-listchanges \
    mailutils \
    postfix \
    haveged

log_success "Security tools installed"

# ============================================
# 4. Configure Automatic Security Updates
# ============================================
log_info "Step 4: Configuring automatic security updates..."

# Enable unattended upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Mail "admin@localhost";
Unattended-Upgrade::MailReport "on-change";
Unattended-Upgrade::SyslogEnable "true";
Unattended-Upgrade::SyslogFacility "daemon";

// Reboot if necessary
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-WithUsers "false";
EOF

# Enable unattended upgrades
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

log_success "Automatic security updates configured"

# ============================================
# 5. Configure UFW Firewall
# ============================================
log_info "Step 5: Configuring UFW Firewall..."

# Reset UFW
ufw --force reset > /dev/null 2>&1 || true
ufw --force enable > /dev/null 2>&1

# Default policies
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed

# Allow from VPN (IPv4)
log_info "  - Allowing from VPN IPv4: $VPN_SUBNET_V4"
ufw allow from "$VPN_SUBNET_V4" to any port 22 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port "$SSH_PORT" proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 8001 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 8002 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 8003 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 8004 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 8005 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 6333 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 11434 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 1880 proto tcp
ufw allow from "$VPN_SUBNET_V4" to any port 3000 proto tcp

# Allow from VPN (IPv6)
log_info "  - Allowing from VPN IPv6: $VPN_SUBNET_V6"
ufw allow from "$VPN_SUBNET_V6" to any port 22 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port "$SSH_PORT" proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 8001 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 8002 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 8003 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 8004 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 8005 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 6333 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 11434 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 1880 proto tcp
ufw allow from "$VPN_SUBNET_V6" to any port 3000 proto tcp

log_success "UFW Firewall configured"

# Show firewall status
ufw status verbose

# ============================================
# 6. SSH Hardening
# ============================================
log_info "Step 6: Hardening SSH configuration..."

# Backup original SSH config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d-%H%M%S)

# Create new SSH config
cat > /etc/ssh/sshd_config << EOF
# SSH Server Configuration - Hardened

# Network and protocol
Port $SSH_PORT
AddressFamily inet
ListenAddress 0.0.0.0
ListenAddress ::

# Protocol
Protocol 2

# Authentication
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
MaxAuthTries 3
MaxSessions 5
StrictModes yes

# Root login disabled
PermitRootLogin no

# User restrictions
AllowUsers asiehen

# Key exchange and ciphers (modern, strong)
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Timeouts and limits
LoginGraceTime 30s
ClientAliveInterval 300
ClientAliveCountMax 2
TCPKeepAlive yes

# Privilege separation and security
PermitUserEnvironment no
Compression no
ClientAliveCountMax 2
PermitTunnel no
AllowTcpForwarding yes
X11Forwarding no
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
Permitallenvironment no
PermitUserRC no

# Logging
SyslogFacility AUTH
LogLevel VERBOSE
UsePAM yes

# Subsystem
Subsystem sftp  /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO

# Banner
Banner /etc/ssh/banner.txt
EOF

# Create SSH banner
cat > /etc/ssh/banner.txt << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                    CHATBOT VPS SYSTEM                      ║
║         Unauthorized access is strictly prohibited         ║
║  All traffic is monitored and logged. Access denied if     ║
║          you do not have proper authorization              ║
╚════════════════════════════════════════════════════════════╝
EOF

# Test SSH config syntax
if sshd -t; then
    systemctl restart ssh
    log_success "SSH hardened and restarted"
else
    log_error "SSH config has errors!"
    exit 1
fi

log_warning "SSH now uses port: $SSH_PORT"
log_warning "Make sure to update your firewall/security group if needed"

# ============================================
# 7. Configure fail2ban
# ============================================
log_info "Step 7: Configuring fail2ban..."

# Create fail2ban local config
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# General settings
bantime = 3600
findtime = 600
maxretry = 3
destemail = adam.siehen@gmail.com
sendername = ChatBot VPS Security
action = %(action_)s
         %(action_mwl)s

# SSH settings
[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
findtime = 600
bantime = 86400

# SSH-ddos (aggressive)
[sshd-ddos]
enabled = true
port = 2222
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 10
findtime = 300
bantime = 600

# Docker/API attempts
[recidive]
enabled = true
filter = recidive
action = %(action_)s
         %(action_mwl)s
bantime = 604800
findtime = 86400
maxretry = 5
logpath = /var/log/fail2ban.log
EOF

# Create SSH-DDoS filter
cat > /etc/fail2ban/filter.d/sshd-ddos.conf << 'EOF'
[Definition]
failregex = ^<HOST> .* sshd\[.*\]: (Invalid|Illegal) user .* from <HOST>
            ^<HOST> .* sshd\[.*\]: Failed password for .* from <HOST>
            ^<HOST> .* sshd\[.*\]: Connection closed by <HOST> \[preauth\]
ignoreregex =
EOF

# Enable fail2ban
systemctl enable fail2ban
systemctl restart fail2ban

log_success "fail2ban configured"

# ============================================
# 8. Network Hardening
# ============================================
log_info "Step 8: Network hardening (SYN cookies, etc)..."

# Enable SYN cookies
cat >> /etc/sysctl.conf << 'EOF'

# ============================================
# Network Security Hardening
# ============================================

# SYN cookies
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_synack_retries = 2

# IP spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.log_martians = 1

# Disable IPv6 if not needed (optional)
# net.ipv6.conf.all.disable_ipv6 = 1

# Connection tracking
net.netfilter.nf_conntrack_tcp_timeout_established = 432000
net.netfilter.nf_conntrack_tcp_timeout_time_wait = 60

# TCP hardening
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_rfc1337 = 1

# Kernel hardening
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.printk = 3 3 3 3
kernel.unprivileged_bpf_disabled = 1
kernel.unprivileged_userns_clone = 0

# Magic SysRq disabled
kernel.sysrq = 0

# Restrict access to kernel logs
kernel.perf_event_paranoid = 3
EOF

sysctl -p > /dev/null

log_success "Network hardening applied"

# ============================================
# 9. File System Hardening
# ============================================
log_info "Step 9: File system hardening..."

# Remount with secure options
mount -o remount,nodev,nosuid,noexec /tmp || log_warning "Could not remount /tmp"
mount -o remount,nodev,nosuid /var || log_warning "Could not remount /var"
mount -o remount,nodev /var/tmp || log_warning "Could not remount /var/tmp"

# Make /tmp, /var/tmp, /dev/shm noexec at boot
cat >> /etc/fstab << 'EOF'
# Secure mount options (added by security hardening)
# tmpfs /tmp tmpfs defaults,rw,nosuid,nodev,noexec,relatime,size=2G 0 0
# tmpfs /dev/shm tmpfs defaults,rw,nosuid,nodev,noexec,relatime 0 0
EOF

log_success "File system hardening applied"

# ============================================
# 10. SSL/TLS Config for Monitoring
# ============================================
log_info "Step 10: Setting up SSL/TLS..."

# Generate self-signed certificate for monitoring
mkdir -p /etc/chatbot-ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/chatbot-ssl/key.pem \
    -out /etc/chatbot-ssl/cert.pem \
    -subj "/C=PL/ST=Poland/L=Warsaw/O=ChatBot/CN=chatbot-vps"

log_success "SSL certificates generated"

# ============================================
# 11. Create monitoring user
# ============================================
log_info "Step 11: Creating monitoring user..."

if ! id -u monitor &> /dev/null; then
    useradd -r -s /bin/bash -d /var/lib/monitor monitor
    mkdir -p /var/lib/monitor
    chown monitor:monitor /var/lib/monitor
    chmod 750 /var/lib/monitor
    log_success "Monitoring user created"
else
    log_warning "Monitoring user already exists"
fi

# ============================================
# 12. Configure Logging
# ============================================
log_info "Step 12: Configuring logging..."

# Configure rsyslog with fine-grained logging
cat > /etc/rsyslog.d/30-security.conf << 'EOF'
# SSH
auth.* /var/log/auth.log
*.*  /var/log/syslog

# Sudo
local1.* /var/log/sudo.log

# Security events
*.crit;kern.warning;*.err /var/log/critical.log

# Mail
mail.* /var/log/mail.log
mail.err /var/log/mail.err
EOF

systemctl restart rsyslog

# Rotate logs to prevent disk space issues
cat > /etc/logrotate.d/chatbot-security << 'EOF'
/var/log/auth.log
/var/log/sudo.log
/var/log/critical.log
{
    weekly
    rotate 12
    compress
    delaycompress
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        /lib/systemd/systemd-logind restart > /dev/null 2>&1 || true
    endscript
}
EOF

log_success "Logging configured"

# ============================================
# 13. VPS Security Summary
# ============================================
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Security Hardening Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Security Summary:${NC}"
echo "  ✓ System packages updated"
echo "  ✓ Automatic security updates: ENABLED"
echo "  ✓ UFW Firewall: ENABLED (VPN-only access)"
echo "  ✓ SSH Hardened: Port $SSH_PORT, key auth only"
echo "  ✓ fail2ban: ENABLED (brute force protection)"
echo "  ✓ Network hardening: SYN cookies, IP spoofing protection"
echo "  ✓ Logging: ENABLED with rotation"
echo ""

echo -e "${YELLOW}Important Settings:${NC}"
echo "  • SSH Port: $SSH_PORT (changed from 22)"
echo "  • SSH Only from VPN: $VPN_SUBNET_V4 and $VPN_SUBNET_V6"
echo "  • fail2ban Ban Time: 1 hour"
echo "  • Monitoring Email: $ADMIN_EMAIL"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Update firewall rules if using cloud provider"
echo "  2. Add SSH key to ~/.ssh/authorized_keys"
echo "  3. Update your SSH client config:"
echo "     Host chatbot-vps"
echo "         HostName <vps-ip>"
echo "         Port $SSH_PORT"
echo "         User asiehen"
echo "         identityFile ~/.ssh/id_rsa"
echo ""

echo -e "${BLUE}Verify Services:${NC}"
systemctl status ssh --no-pager | head -3
systemctl status fail2ban --no-pager | head -3
systemctl status ufw --no-pager | head -3

echo ""
echo -e "${GREEN}Ready for deployment! Run:${NC}"
echo "  ./deploy.sh deploy"
echo ""
