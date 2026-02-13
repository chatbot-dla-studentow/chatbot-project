#!/bin/bash
# WireGuard Setup dla chatbot-project
# Run on VPS: sudo bash wireguard-setup.sh

set -e

echo "=== WireGuard Server Setup ==="

# Update system
apt-get update && apt-get upgrade -y

# Install WireGuard
apt-get install -y wireguard wireguard-tools linux-headers-$(uname -r)

# Generate server keys
cd /etc/wireguard
umask 077
wg genkey | tee privatekey | wg pubkey > publickey

PRIVATE_KEY=$(cat privatekey)
PUBLIC_KEY=$(cat publickey)

echo "Generated WireGuard Keys:"
echo "Private Key: $PRIVATE_KEY"
echo "Public Key: $PUBLIC_KEY"
echo ""
echo "⚠️  SAVE THESE KEYS SOMEWHERE SECURE!"
echo ""

# Create wg0.conf
cat > wg0.conf << EOF
[Interface]
PrivateKey = $PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = 51820
SaveConfig = false

# Client connection (GitHub Actions)
[Peer]
PublicKey = di0wRfrPoUGMBY46n5f8/1VGsZ9bhAPSab3tmiLTzXc=
AllowedIPs = 10.0.0.2/32
PersistentKeepalive = 25
EOF

chmod 600 wg0.conf

# Enable and start WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0

# Configure firewall
ufw allow 51820/udp comment "WireGuard VPN"
ufw allow 22/tcp comment "SSH over VPN" || ufw allow from 10.0.0.0/24 to any port 22

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

# Add NAT rules
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i wg0 -j ACCEPT
iptables -A FORWARD -o wg0 -j ACCEPT

# Save iptables rules
apt-get install -y iptables-persistent
netfilter-persistent save

echo ""
echo "=== WireGuard Setup Complete ==="
echo ""
echo "Server IP: 10.0.0.1"
echo "Listen Port: 51820"
echo ""
wg show

# Maintainers: Adam Siehen, Patryk Boguski
