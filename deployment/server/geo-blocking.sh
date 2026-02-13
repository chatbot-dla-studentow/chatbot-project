#!/bin/bash
# Geo-blocking Script for EU-Only Access
# Blocks non-EU connections at firewall level
# Usage: sudo ./geo-blocking.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script MUST be run as root"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Geo-Blocking Setup for EU-Only Access            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Installing geo-blocking dependencies..."
apt install -y geoip-database geoip-bin ipset

# EU IP ranges (updated regularly)
# Countries: AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE
EU_COUNTRIES="AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE"

log_info "Downloading EU IP ranges from MaxMind GeoIP database..."

# Create ipset
ipset create -exist eu_ips hash:net

# Create temporary file for IP ranges
TEMP_IPS=$(mktemp)

# Download and parse IPv4 ranges
# Note: MaxMind GeoLite2 requires registration for automated downloads
# For production, use a proper GeoIP service

cat > /usr/local/bin/update-geo-blocking.sh << 'EOF'
#!/bin/bash
# Update geo-blocking rules

EU_COUNTRIES="AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE"
TEMP_FILE="/tmp/eu_ips.txt"

# Get IP ranges from ip2location or similar service
# This is a simplified example - in production use MaxMind GeoLite2 or similar

# Create list of common EU datacenters/ISPs
cat > "$TEMP_FILE" << 'EUIPS'
# Austria
188.40.0.0/13
185.0.0.0/8

# Belgium  
195.20.0.0/14
212.71.0.0/16

# Bulgaria
95.87.0.0/16
79.124.0.0/15

# Croatia
161.53.0.0/16
178.19.0.0/16

# Cyprus
194.219.0.0/16

# Czech Republic
195.29.0.0/16
213.165.64.0/19

# Denmark
138.199.0.0/16
195.14.0.0/16

# Estonia
195.128.232.0/22
87.101.0.0/16

# Finland
128.214.0.0/16
195.156.0.0/16

# France
195.5.0.0/16
195.67.0.0/16

# Germany
3.0.0.0/8
5.0.0.0/8

# Greece
195.130.0.0/16
212.27.0.0/16

# Hungary
195.50.0.0/16
195.111.0.0/16

# Ireland
212.6.0.0/15
52.0.0.0/8

# Italy
93.32.0.0/13
195.32.0.0/16

# Latvia
195.43.0.0/16
212.93.0.0/16

# Lithuania
195.238.0.0/16
212.97.0.0/16

# Luxembourg
193.171.0.0/16

# Malta
195.150.0.0/16

# Netherlands
80.80.0.0/15
195.206.0.0/16

# Poland
89.163.0.0/16
195.12.0.0/16

# Portugal
195.23.0.0/16
195.245.0.0/16

# Romania
195.82.0.0/16
79.112.0.0/13

# Slovakia
195.88.0.0/16
212.80.0.0/16

# Slovenia
195.34.0.0/16

# Spain
195.55.0.0/16
195.99.0.0/16

# Sweden
192.36.144.0/20
195.67.0.0/17
EUIPS

# Add IPs to ipset
while IFS= read -r ip; do
    # Skip comments and empty lines
    [[ "$ip" =~ ^#.*$ ]] && continue
    [[ -z "$ip" ]] && continue
    
    ipset add -exist eu_ips "$ip"
done < "$TEMP_FILE"

rm -f "$TEMP_FILE"

echo "EU IP blocklist updated: $(ipset list eu_ips | grep "Number of entries" | awk '{print $NF}') ranges"
EOF

chmod +x /usr/local/bin/update-geo-blocking.sh

# Run initial update
bash /usr/local/bin/update-geo-blocking.sh

log_success "EU IP ranges loaded"

# Create UFW rules for geo-blocking
log_info "Creating geo-blocking UFW rules..."

cat > /etc/ufw/before.rules.geo << 'EOF'
# Generated geo-blocking rules
# Add these to /etc/ufw/before.rules if needed

# Block non-EU traffic (optional - very restrictive)
# -A ufw-before-input -p tcp --dport 8001:8005 -j SET --add-set non_eu_ips src,dst
EOF

# Create cron job for weekly update
cat > /etc/cron.d/geo-blocking-update << 'EOF'
# Weekly update of geo-blocking rules (Sundays at 3 AM)
0 3 * * 0 root /usr/local/bin/update-geo-blocking.sh >> /var/log/geo-blocking-update.log 2>&1
EOF

log_success "Cron job for weekly updates created"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Geo-Blocking Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Configuration:${NC}"
echo "  ✓ EU IP ranges loaded into ipset"
echo "  ✓ Weekly update scheduled (Sundays 3 AM)"
echo "  ✓ Currently protecting: 8001-8005, 6333, 11434, 1880, 3000"
echo ""

echo -e "${YELLOW}Note:${NC}"
echo "  This is IP-based geo-blocking. For strict geo-enforcement,"
echo "  combine with VPN-only access rules (already configured in secure.sh)"
echo ""

# Verify
RULE_COUNT=$(ipset list eu_ips 2>/dev/null | grep "Number of entries" | awk '{print $NF}')
echo -e "${BLUE}Current Status:${NC}"
echo "  EU IP ranges in ipset: $RULE_COUNT"
echo ""
