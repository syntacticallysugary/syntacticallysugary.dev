# ── OCI Snagger Configuration ──────────────────────────────────────────────────

COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaa4tza2b2zb5ohkkmhlg73glqpugwuhiqaefzqhwepw55r2dp74gtq"

# All three Chicago ADs — snag.py rotates through them each attempt.
AVAILABILITY_DOMAINS = [
    "AcSx:US-CHICAGO-1-AD-1",
    "AcSx:US-CHICAGO-1-AD-2",
    "AcSx:US-CHICAGO-1-AD-3",
]

# Networking → Virtual Cloud Networks → your VCN → Subnets → OCID
# Still needs a VCN — run the wizard then re-run preflight.py to get this value.
SUBNET_ID = "ocid1.subnet.oc1.us-chicago-1.aaaaaaaay32wuvcjdugysxerwf52gtai4hrrd7ovjpaoikrb622jz4h4twwa"

# Ubuntu 24.04 Minimal aarch64 — current as of 2026-03-31
IMAGE_ID = "ocid1.image.oc1.us-chicago-1.aaaaaaaaprys63xvlemh3l5wzfjrgbu6vr3mvnz7feeqa4wfjfjhparubwua"

SSH_PUBLIC_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDRI9GG4x1z3l+Fdb8e65zYEAOXHKBpAF1w2rgeOZ62k github-key"

# ── Instance specs ─────────────────────────────────────────────────────────────
INSTANCE_NAME  = "erpnext-free"
OCPUS          = 4
MEMORY_GB      = 24
BOOT_VOLUME_GB = 180

# ── Polling ────────────────────────────────────────────────────────────────────
RETRY_SECONDS  = 45
