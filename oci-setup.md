# OCI Infrastructure — Syntactically Sugary

## Account Status

- **Account type:** Individual PAYGO (upgraded from Always Free)
- **Home region:** US Midwest (Chicago) — `us-chicago-1`
- **Availability domains:** `AcSx:US-CHICAGO-1-AD-1`, `AD-2`, `AD-3`
- **Tenancy OCID:** `ocid1.tenancy.oc1..aaaaaaaa4tza2b2zb5ohkkmhlg73glqpugwuhiqaefzqhwepw55r2dp74gtq`
- **VCN:** Base (10.0.0.0/16) — public and private subnets provisioned

---

## Targeted Infrastructure (Planned)

| Resource | Configuration | Purpose |
|---|---|---|
| ARM Ampere A1 VM | 4 OCPU · 24 GB RAM · Ubuntu 24.04 | ERPNext + MariaDB + Redis |
| Public subnet | `ocid1.subnet.oc1.us-chicago-1.aaaaaaaay32wu...` | Internet-facing |
| Private subnet | `ocid1.subnet.oc1.us-chicago-1.aaaaaaaajj5zo...` | Internal services |
| Object Storage | 30 GB (10 Standard + 10 Infrequent + 10 Archive) | ERPNext DB backups |

**Snag script** is running at `~/Dev/synsug/oci-snag/` polling every 45 seconds across all
three Chicago ADs. Script exits and notifies on success.

---

## OCI Always Free Resources (PAYGO account)

Always Free resources cost $0 permanently as long as usage stays within the limits below.
PAYGO means you have access to paid shapes if needed — you are only billed for what you
provision above the Always Free limits.

### Compute

| Shape | Specs | Quantity |
|---|---|---|
| **ARM Ampere A1 Flex** (`VM.Standard.A1.Flex`) | 4 OCPU + 24 GB RAM total — split across 1–4 VMs however you like | 1 pool |
| **AMD Micro** (`VM.Standard.E2.1.Micro`) | 1/8 OCPU · 1 GB RAM · 50 Mbps internet | 2 VMs |

> **Idle reclamation warning:** Oracle will reclaim Always Free VMs where CPU, network,
> and memory (A1 only) all stay below 20% utilization for a 7-day period. ERPNext running
> MariaDB and Redis will easily clear this threshold, but note it for any lightweight VMs.

### Block Storage

| Resource | Limit |
|---|---|
| Total block volume storage (boot + data combined) | **200 GB** |
| Volume backups | 5 (boot + block combined) |
| Minimum boot volume per VM | 47 GB |

### Object Storage

| Tier | Limit |
|---|---|
| Standard | 10 GB |
| Infrequent Access | 10 GB |
| Archive | 10 GB |
| API requests | 50,000/month |

> Use Archive tier for ERPNext database backups — they are infrequently accessed and compress well.

### Databases

| Service | Allowance |
|---|---|
| **Oracle Autonomous DB** | 2 instances · 20 GB storage · 1 OCPU each |
| **MySQL HeatWave** | 1 instance · 50 GB storage + 50 GB backup |
| **Oracle NoSQL** | 3 tables · 25 GB/table · 133M reads + 133M writes/month |

> ERPNext uses its own MariaDB installed on the VM — these managed database offerings are
> free slots available for other apps.

### Networking

| Resource | Allowance |
|---|---|
| Flexible Load Balancer | 1 × 10 Mbps (16 listeners, 16 backend sets) |
| Network Load Balancer | 1 |
| Outbound data transfer | **10 TB/month** |
| Site-to-Site VPN | 50 IPSec connections |
| Bastion | Free (time-limited SSH to private resources) |

### Security & Secrets

| Resource | Allowance |
|---|---|
| Vault secrets | 150 |
| HSM-protected key versions | 20 |
| Software-protected key versions | Unlimited |
| TLS Certificates | 150 certs · 5 certificate authorities |

### Observability

| Resource | Allowance |
|---|---|
| Monitoring (ingestion) | 500 million datapoints/month |
| Monitoring (retrieval) | 1 billion datapoints/month |
| Notifications | 1 million HTTPS + 1,000 email/month |
| Email Delivery | 3,000 emails/month |
| APM tracing | 1,000 events + 10 synthetic monitor runs/hour |
| Logging | 10 GB/month |

### Automation & Tooling

| Resource | Allowance |
|---|---|
| Resource Manager (Terraform) | 100 stacks · 2 concurrent jobs |
| Connector Hub | 2 connectors |
| Fleet Application Management | 25 managed resources/month |

---

## Storage Allocation Problem

The snag script is currently configured to request a **180 GB boot volume**
(`BOOT_VOLUME_GB = 180` in `oci-snag/config.py`). That leaves only 20 GB for everything
else — not enough for a second VM (minimum 47 GB boot volume).

### Option A — Two A1 VMs (recommended if second app is compute-heavy)

```
200 GB total block storage
├─ 100 GB  →  A1 VM 1 (2 OCPU · 12 GB RAM) — ERPNext
└─ 100 GB  →  A1 VM 2 (2 OCPU · 12 GB RAM) — second app
```

Requires changing `BOOT_VOLUME_GB = 100` in `oci-snag/config.py` before the instance lands,
and provisioning VM 2 manually afterward.

### Option B — One large A1 VM + AMD Micro pair (if second app is lightweight)

```
200 GB total block storage
├─ 100 GB  →  A1 VM (4 OCPU · 24 GB RAM) — ERPNext + second app via Docker
├─  47 GB  →  AMD Micro VM 1 boot (1 GB RAM) — lightweight service / reverse proxy
└─  53 GB  →  AMD Micro VM 2 boot (1 GB RAM) — lightweight service
```

### Option C — One large A1 VM + separate data volume (if second app doesn't need its own VM)

```
200 GB total block storage
├─  50 GB  →  A1 VM boot (OS only)
├─ 100 GB  →  Attached block volume (MariaDB data, ERPNext files)
└─  50 GB  →  Second attached block volume or second VM boot
```

---

## Decision Needed Before Instance Lands

**Update `BOOT_VOLUME_GB` in `oci-snag/config.py` before the snag script succeeds.**
Once an instance is provisioned, the boot volume size is set. Changing it later requires
stopping the instance and resizing, which is possible but annoying.

Current setting: `180` — change to `100` to preserve flexibility.

---

## Post-Provisioning Checklist

When the snag script succeeds, the log will show:

```
SUCCESS on attempt #XXXX!  Instance ocid1.instance...  state=PROVISIONING
```

Steps immediately after:

1. **OCI Console → Compute → Instances** — note the public IP address
2. **SSH in:** `ssh ubuntu@<public-ip>` using `~/.ssh/id_ed25519`
3. **Open firewall ports** — OCI Console → Networking → VCNs → Base → Security Lists:
   - Ingress: TCP port 80 (HTTP)
   - Ingress: TCP port 443 (HTTPS)
   - Port 22 (SSH) should already be open
4. **Install ERPNext** via Docker or bench (decide which before you start)
5. **Point domain** — `office.syntacticallysugary.dev` or similar subdomain → instance IP
6. **Set up Object Storage backup** — configure ERPNext to push daily DB backups to the
   Archive tier bucket
7. **Set $1 budget alert** — OCI Console → Billing → Budgets → alert if spend exceeds $1

---

## Key File Locations

| File | Path |
|---|---|
| Snag script | `~/Dev/synsug/oci-snag/snag.py` |
| Snag config | `~/Dev/synsug/oci-snag/config.py` |
| Snag log | `~/Dev/synsug/oci-snag/snag.log` |
| OCI credentials | `~/.oci/config` |
| OCI private key | `~/.oci/oci_api_key.pem` |
| SSH key | `~/.ssh/id_ed25519` |
