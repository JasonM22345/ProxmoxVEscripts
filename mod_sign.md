The error "req: Use -help for summary" suggests that there might be an issue with the command syntax for `openssl req`. Let’s break down the process into more manageable steps and ensure the correct syntax is used.

### 1. Install `openssl`

First, ensure `openssl` is installed:

```bash
sudo apt-get install openssl
```

### 2. Generate the Key Pair

Next, generate a private key and a self-signed certificate. Run the following commands separately to avoid any syntax errors:

```bash
openssl genpkey -algorithm RSA -out MOK.priv -aes256
openssl req -new -x509 -key MOK.priv -outform DER -out MOK.der -days 36500 -subj "/CN=Custom Module Signing Key/"
```

Let’s break these commands down:
- `openssl genpkey -algorithm RSA -out MOK.priv -aes256`: This generates a private key using RSA and saves it to `MOK.priv`.
- `openssl req -new -x509 -key MOK.priv -outform DER -out MOK.der -days 36500 -subj "/CN=Custom Module Signing Key/"`: This creates a new certificate signing request and self-signs it, creating a certificate valid for 100 years, and outputs it in DER format.

### 3. Sign the Module

Now, sign the i915 module using `kmodsign`. First, locate the i915 module:

```bash
modinfo -n i915
```

Then sign the module (replace `/path/to/i915.ko` with the actual path obtained from the `modinfo` command):

```bash
sudo kmodsign sha512 MOK.priv MOK.der /path/to/i915.ko
```

### 4. Enroll the Key in UEFI

1. Install `mokutil` if it’s not already installed:

```bash
sudo apt-get install mokutil
```

2. Import the key:

```bash
sudo mokutil --import MOK.der
```

3. You will be prompted to create a password. This password will be used in the next steps.

4. Reboot the system. During boot, the MOK Manager will appear. Follow the prompts to enroll the key:
   - Select "Enroll MOK".
   - Select "Continue".
   - Enter the password you created earlier.
   - Confirm and reboot.

This should resolve the issue with the i915 module verification failing due to a missing signature or key.