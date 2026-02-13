#!/bin/bash
# SSH Secure Setup - uruchomić w console'u VPS
# Włącza SSH ale z maksymalnym bezpieczeństwem

set -e

echo "=== SSH Secure Setup ==="

# 1. Włącz SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# 2. Edytuj sshd_config
sudo tee /etc/ssh/sshd_config > /dev/null << 'EOF'
# Port niestandardowy
Port 2222

# Tylko na VPN interface
ListenAddress 10.0.0.1

# Bezpieczeństwo
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
KeyboardInteractiveAuthentication no
GSSAPIAuthentication no
UsePAM yes

# Wzmocnione ustawienia
Protocol 2
X11Forwarding no
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
PermitUserEnvironment no
Compression delayed
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 10

# Hostkey
HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_rsa_key

# Kryptografia (nowoczesna)
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes-256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Logowanie
SyslogFacility AUTH
LogLevel VERBOSE

# Subsystem
Subsystem sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO
EOF

# 3. Sprawdź składnię
sudo sshd -t
echo "✅ SSH config syntax OK"

# 4. Zrestartuj SSH
sudo systemctl restart ssh
sudo systemctl status ssh

# 5. Dodaj fail2ban dla SSH
sudo apt-get install -y fail2ban

# Konfiguruj fail2ban dla SSH na porcie 2222
sudo tee /etc/fail2ban/jail.d/sshd.conf > /dev/null << 'EOF'
[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
findtime = 600
bantime = 3600
EOF

# Zrestartuj fail2ban
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# 6. Firewall - zezwól na SSH z VPN
sudo ufw allow from 10.0.0.0/24 to 10.0.0.1 port 2222 comment "SSH from VPN"
sudo ufw status | grep 2222

echo ""
echo "=== SSH Setup Complete ==="
echo ""
echo "SSH Configuration:"
echo "  - Port: 2222"
echo "  - Listen: 10.0.0.1 (tylko VPN)"
echo "  - Auth: Key-based only"
echo "  - Root login: DISABLED"
echo "  - Password auth: DISABLED"
echo ""
echo "Fail2ban:"
echo "  - sshd protection: 3 tries = 1h ban"
echo "  - Status: $(sudo systemctl status fail2ban | grep Active)"
echo ""
echo "Test połączenia (z Windows, gdy WireGuard jest active):"
echo "  ssh -i \$env:USERPROFILE\.ssh\chatbot_vps_new -p 2222 ubuntu@10.0.0.1"
echo ""
