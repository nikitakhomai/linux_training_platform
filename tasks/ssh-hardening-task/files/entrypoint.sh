#!/bin/bash

echo "========================================="
echo "🐧 SSH Hardening Training Container"
echo "========================================="
echo ""
echo "Your task: Harden the SSH configuration!"
echo ""
echo "Current insecure configuration:"
echo "  - Port: 22 (default)"
echo "  - Root login: ENABLED (INSECURE)"
echo "  - Password auth: ENABLED (INSECURE)"
echo "  - Max attempts: 6 (too high)"
echo "  - AllowUsers: root only"
echo ""
echo "What you need to do:"
echo "  1. Edit /etc/ssh/sshd_config"
echo "  2. Make it SECURE:"
echo "     - PermitRootLogin no"
echo "     - PasswordAuthentication no"
echo "     - Port 2222"
echo "     - AllowUsers student"
echo "     - MaxAuthTries 3"
echo "  3. Restart SSH: sudo systemctl restart ssh"
echo "  4. Check your config: sudo sshd -t"
echo ""
echo "When ready, run validation:"
echo "  /usr/local/bin/check.sh"
echo ""
echo "========================================="

# Generate SSH host keys if not present
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    ssh-keygen -A
fi

# Start SSH server in foreground
exec "$@"
