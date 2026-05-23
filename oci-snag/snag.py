#!/usr/bin/env python3
"""
OCI ARM Instance Snagger
Polls Oracle Cloud API until an Always Free ARM Ampere A1 instance becomes available.
Exits 0 on success, 1 on a config/auth error that won't fix itself with retries.
"""

import logging
import subprocess
import sys
import time

import oci

import config


# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("snag.log"),
    ],
)
log = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def notify(message: str) -> None:
    """Ring the terminal bell and attempt a desktop notification."""
    # \a = terminal bell; works even over SSH if your terminal has audio enabled
    print(f"\a\n{'=' * 60}\n  {message}\n{'=' * 60}\n")
    try:
        subprocess.run(["notify-send", "--urgency=critical", "OCI Snagger", message],
                       check=False, timeout=5)
    except FileNotFoundError:
        pass  # notify-send absent (headless server) — terminal bell is enough


def _build_launch_details(availability_domain: str) -> oci.core.models.LaunchInstanceDetails:
    return oci.core.models.LaunchInstanceDetails(
        availability_domain=availability_domain,
        compartment_id=config.COMPARTMENT_ID,
        display_name=config.INSTANCE_NAME,
        shape="VM.Standard.A1.Flex",
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=config.OCPUS,
            memory_in_gbs=config.MEMORY_GB,
        ),
        # Separate source_details lets us set boot volume size.
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            source_type="image",
            image_id=config.IMAGE_ID,
            boot_volume_size_in_gbs=config.BOOT_VOLUME_GB,
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=config.SUBNET_ID,
            assign_public_ip=True,
        ),
        metadata={"ssh_authorized_keys": config.SSH_PUBLIC_KEY},
    )


def _is_capacity_error(e: oci.exceptions.ServiceError) -> bool:
    msg = (e.message or "").lower()
    return e.status == 500 and (
        "host capacity" in msg
        or "out of capacity" in msg
        or "insufficient capacity" in msg
    )


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    # Sanity-check config before wasting any API calls.
    for field in ("COMPARTMENT_ID", "SUBNET_ID", "IMAGE_ID", "SSH_PUBLIC_KEY"):
        if "CHANGE_ME" in getattr(config, field):
            log.error("config.py: %s is still CHANGE_ME. Run preflight.py first.", field)
            sys.exit(1)

    oci_config = oci.config.from_file()
    compute    = oci.core.ComputeClient(oci_config)
    ads        = config.AVAILABILITY_DOMAINS

    log.info("Starting — polling every %ds for %s (%d OCPU / %d GB RAM / %d GB disk)",
             config.RETRY_SECONDS, config.INSTANCE_NAME,
             config.OCPUS, config.MEMORY_GB, config.BOOT_VOLUME_GB)
    log.info("Rotating across %d availability domains: %s", len(ads), ads)
    log.info("Tail the log:  tail -f snag.log")
    log.info("Stop with:     Ctrl+C  (or kill the process)")

    attempt = 0
    while True:
        attempt += 1
        ad = ads[(attempt - 1) % len(ads)]
        log.info("Attempt #%d — AD: %s", attempt, ad)
        details = _build_launch_details(ad)
        try:
            instance = compute.launch_instance(launch_instance_details=details).data
            msg = (
                f"SUCCESS on attempt #{attempt}!  "
                f"Instance {instance.id}  state={instance.lifecycle_state}  "
                f"Check OCI Console → Compute → Instances"
            )
            log.info(msg)
            notify(msg)
            sys.exit(0)

        except oci.exceptions.ServiceError as e:
            if _is_capacity_error(e):
                log.info("No capacity yet. Retry in %ds…", config.RETRY_SECONDS)

            elif e.status == 429:
                backoff = config.RETRY_SECONDS * 3
                log.warning("Rate-limited (429). Backing off %ds.", backoff)
                time.sleep(backoff)
                continue

            elif e.status in (401, 403):
                log.error("Auth/permission error %d: %s — %s", e.status, e.code, e.message)
                log.error("Check ~/.oci/config and that your user has 'manage instances' permission.")
                sys.exit(1)

            else:
                log.error("Unexpected OCI error %d (%s): %s", e.status, e.code, e.message)
                log.error("Pausing %ds before retry (may self-resolve).", config.RETRY_SECONDS * 2)
                time.sleep(config.RETRY_SECONDS * 2)
                continue

        except oci.exceptions.RequestException as e:
            log.warning("Network error: %s — retry in %ds.", e, config.RETRY_SECONDS)

        except Exception as e:
            log.warning("Unhandled %s: %s — retry in %ds.", type(e).__name__, e, config.RETRY_SECONDS)

        time.sleep(config.RETRY_SECONDS)


if __name__ == "__main__":
    main()
