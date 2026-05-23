#!/usr/bin/env python3
"""
OCI Preflight — discover the OCIDs you need before running snag.py.

Usage:
    python3 preflight.py

Reads ~/.oci/config for credentials.
"""

import sys
import oci
import config


def _section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


def check_config() -> oci.config.DEFAULT_CONFIG:
    try:
        cfg = oci.config.from_file()
        oci.config.validate_config(cfg)
        _section("OCI Config (~/.oci/config)")
        print(f"  User      : {cfg['user']}")
        print(f"  Tenancy   : {cfg['tenancy']}")
        print(f"  Region    : {cfg['region']}")
        print(f"  Key file  : {cfg['key_file']}")
        return cfg
    except Exception as e:
        print(f"[ERROR] ~/.oci/config problem: {e}")
        print("  Run: oci setup config   — or create the file manually.")
        sys.exit(1)


def list_availability_domains(identity: oci.identity.IdentityClient, tenancy_id: str) -> None:
    _section("Availability Domains")
    ads = identity.list_availability_domains(compartment_id=tenancy_id).data
    for ad in ads:
        marker = "  ← set AVAILABILITY_DOMAIN to this" if len(ads) == 1 else ""
        print(f"  {ad.name}{marker}")


def list_vcns_and_subnets(network: oci.core.VirtualNetworkClient, compartment_id: str) -> None:
    _section("VCNs and Subnets")
    vcns = network.list_vcns(compartment_id=compartment_id).data
    if not vcns:
        print("  No VCNs found — create one first:")
        print("  OCI Console → Networking → Virtual Cloud Networks → Start VCN Wizard")
        return
    for vcn in vcns:
        print(f"\n  VCN: {vcn.display_name}  ({vcn.cidr_block})")
        subnets = network.list_subnets(compartment_id=compartment_id, vcn_id=vcn.id).data
        for sn in subnets:
            pub = "PUBLIC " if not sn.prohibit_public_ip_on_vnic else "private"
            print(f"    {pub} subnet: {sn.display_name}")
            print(f"           OCID : {sn.id}")


def list_arm_images(compute: oci.core.ComputeClient, compartment_id: str) -> None:
    _section("Ubuntu ARM Images (VM.Standard.A1.Flex compatible)")
    images = compute.list_images(
        compartment_id=compartment_id,
        operating_system="Canonical Ubuntu",
        shape="VM.Standard.A1.Flex",
        sort_by="TIMECREATED",
        sort_order="DESC",
    ).data

    if not images:
        print("  No matching images found — try the OCI Console:")
        print("  Compute → Images → Platform Images → filter by Ubuntu + aarch64")
        return

    for img in images[:5]:   # show 5 most recent
        print(f"  {img.display_name}")
        print(f"    OCID: {img.id}")


def check_current_config_values() -> None:
    _section("Your current config.py values")
    fields = [
        ("COMPARTMENT_ID",     config.COMPARTMENT_ID),
        ("AVAILABILITY_DOMAINS", str(config.AVAILABILITY_DOMAINS)),
        ("SUBNET_ID",          config.SUBNET_ID),
        ("IMAGE_ID",           config.IMAGE_ID),
    ]
    all_set = True
    for name, val in fields:
        if "CHANGE_ME" in val:
            print(f"  ✗ {name}: NOT SET")
            all_set = False
        else:
            print(f"  ✓ {name}: {val[:60]}…" if len(val) > 60 else f"  ✓ {name}: {val}")
    if all_set:
        print("\n  All required fields set — you're ready to run snag.py!")
    else:
        print("\n  Fill in the CHANGE_ME values in config.py, then re-run preflight.py.")


def main() -> None:
    print("\nOCI Preflight Check")
    cfg = check_config()
    tenancy_id = cfg["tenancy"]
    compartment_id = config.COMPARTMENT_ID
    if "CHANGE_ME" in compartment_id:
        compartment_id = tenancy_id   # fall back to root

    identity = oci.identity.IdentityClient(cfg)
    compute  = oci.core.ComputeClient(cfg)
    network  = oci.core.VirtualNetworkClient(cfg)

    list_availability_domains(identity, tenancy_id)
    list_vcns_and_subnets(network, compartment_id)
    list_arm_images(compute, compartment_id)
    check_current_config_values()
    print()


if __name__ == "__main__":
    main()
