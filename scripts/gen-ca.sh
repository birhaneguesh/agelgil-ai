#!/usr/bin/env bash
# Per-deployment CA and leaf, fixed validity per AGELGIL-MVP-FINAL §5.
#   CA   : notBefore 2020-01-01, notAfter 2040-01-01
#   Leaf : notBefore 2020-01-01, notAfter 2035-01-01
#   SAN  : agelgil.internal, *.agelgil.internal, localhost, 127.0.0.1,
#          plus each --ip and --dns argument.
# Requires OpenSSL 3.0+.
#
# MSYS_NO_PATHCONV=1 stops Git Bash from rewriting "-subj /CN=..." into
# "C:/Program Files/Git/CN=...".
# mktemp -d -p "$TARGET" keeps the workdir relative so openssl opens files
# it can actually see even with MSYS_NO_PATHCONV=1.
# Extensions are written with section headers and passed via -extensions;
# openssl ca's -extfile without -extensions looks for a [default] section
# that would otherwise be absent.
export MSYS_NO_PATHCONV=1
set -euo pipefail

TARGET="${TARGET:-out}"
CN="agelgil.internal"
EXTRA_DNS=()
EXTRA_IPS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ip)  EXTRA_IPS+=("$2"); shift 2 ;;
    --dns) EXTRA_DNS+=("$2"); shift 2 ;;
    -h|--help) echo "usage: $0 [--ip <ipv4>]... [--dns <name>]..." >&2; exit 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! openssl version | grep -qE '^OpenSSL (3\.|[4-9]\.)'; then
  echo "error: OpenSSL 3.0+ required (found: $(openssl version))" >&2
  exit 1
fi

mkdir -p "$TARGET"
WORK=$(mktemp -d -p "$TARGET")
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/ca.cnf" << CONF
[ca]
default_ca = CA_default
[CA_default]
dir = $WORK
database = \$dir/index.txt
new_certs_dir = \$dir/newcerts
serial = \$dir/serial
default_md = sha256
policy = policy_any
[policy_any]
commonName = optional
CONF
mkdir -p "$WORK/newcerts"
: > "$WORK/index.txt"
echo 1000 > "$WORK/serial"

openssl genrsa -out "$TARGET/ca.key" 4096 2>/dev/null
openssl req -new -key "$TARGET/ca.key" -subj "/CN=Agelgil Local CA" -out "$WORK/ca.csr"

cat > "$WORK/ca.ext" << EXT
[v3_ca]
basicConstraints = critical, CA:TRUE, pathlen:0
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
EXT

openssl ca -batch -selfsign -notext -config "$WORK/ca.cnf" \
  -keyfile "$TARGET/ca.key" -in "$WORK/ca.csr" -out "$TARGET/ca.crt" \
  -extfile "$WORK/ca.ext" -extensions v3_ca \
  -startdate 20200101000000Z -enddate 20400101000000Z

openssl genrsa -out "$TARGET/leaf.key" 2048 2>/dev/null
openssl req -new -key "$TARGET/leaf.key" -subj "/CN=$CN" -out "$WORK/leaf.csr"

SAN="DNS:$CN,DNS:*.$CN,DNS:localhost,IP:127.0.0.1"
for d in "${EXTRA_DNS[@]}"; do SAN="$SAN,DNS:$d"; done
for i in "${EXTRA_IPS[@]}"; do SAN="$SAN,IP:$i"; done

cat > "$WORK/leaf.ext" << EXT
[v3_leaf]
basicConstraints = critical, CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = $SAN
EXT

openssl ca -batch -notext -config "$WORK/ca.cnf" \
  -cert "$TARGET/ca.crt" -keyfile "$TARGET/ca.key" \
  -in "$WORK/leaf.csr" -out "$TARGET/leaf.crt" \
  -extfile "$WORK/leaf.ext" -extensions v3_leaf \
  -startdate 20200101000000Z -enddate 20350101000000Z

openssl verify -CAfile "$TARGET/ca.crt" "$TARGET/leaf.crt"
