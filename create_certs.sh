#!/bin/bash

# Configuration
CA_PASSWORD="YOUR_CA_PASSWORD"
SERVER_PASSWORD="YOUR_SERVER_PASSWORD"
COUNTRY="US"
STATE="YourState"
CITY="YourCity"
ORGANIZATION="YourOrganization"
UNIT="YourUnit"
CA_COMMON_NAME="YourCA"
SERVER_COMMON_NAME="yourdomain.com"
DAYS_VALID=365
EXT_FILE="v3.ext"

# Directories
CA_DIR="ca"
SERVER_DIR="server"

# Create directories
mkdir -p $CA_DIR $SERVER_DIR

# Step 1: Create CA private key
openssl genpkey -algorithm RSA -out $CA_DIR/ca.key -aes256 -pass pass:$CA_PASSWORD

# Step 2: Create CA self-signed root certificate
openssl req -x509 -new -nodes -key $CA_DIR/ca.key -sha256 -days $((DAYS_VALID * 10)) -out $CA_DIR/ca.pem -passin pass:$CA_PASSWORD -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$UNIT/CN=$CA_COMMON_NAME"

# Step 3: Create server private key
openssl genpkey -algorithm RSA -out $SERVER_DIR/server.key -aes256 -pass pass:$SERVER_PASSWORD

# Step 4: Create server certificate signing request (CSR)
openssl req -new -key $SERVER_DIR/server.key -out $SERVER_DIR/server.csr -passin pass:$SERVER_PASSWORD -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$UNIT/CN=$SERVER_COMMON_NAME"

# Step 5: Create configuration file for certificate extensions
cat > $EXT_FILE <<- EOM
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $SERVER_COMMON_NAME
DNS.2 = www.$SERVER_COMMON_NAME
EOM

# Step 6: Sign server certificate with CA
openssl x509 -req -in $SERVER_DIR/server.csr -CA $CA_DIR/ca.pem -CAkey $CA_DIR/ca.key -CAcreateserial -out $SERVER_DIR/server.crt -days $DAYS_VALID -sha256 -extfile $EXT_FILE -passin pass