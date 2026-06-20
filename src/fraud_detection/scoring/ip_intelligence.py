"""IP Intelligence - detects VPN, TOR, proxy, and datacenter IPs. Weight: 10%."""

import ipaddress

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext

# Known datacenter/cloud IP ranges (simplified - in production, use a proper IP intelligence service)
DATACENTER_PREFIXES = [
    "34.", "35.",   # Google Cloud
    "52.", "54.",   # AWS
    "104.16",       # Cloudflare
    "13.64",        # Azure
]

# Private/reserved ranges that shouldn't appear in production
SUSPICIOUS_PRIVATE_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


class IPIntelligence(ScoringModule):
    name = "ip_intelligence"
    weight = 0.10
    description = "Detects VPN, TOR, proxy, and datacenter IP addresses"

    async def score(self, context: TransactionContext) -> ScoringResult:
        signals: list[str] = []
        score = 0.0

        if not context.ip_address:
            return ScoringResult(score=5, confidence=0.3, signals=["No IP address provided"])

        ip_str = context.ip_address

        # Check metadata flags (typically set by upstream IP intelligence service)
        metadata = context.metadata
        is_vpn = metadata.get("ip_is_vpn", False)
        is_tor = metadata.get("ip_is_tor", False)
        is_proxy = metadata.get("ip_is_proxy", False)
        is_datacenter = metadata.get("ip_is_datacenter", False)

        # TOR exit node - highest risk
        if is_tor:
            score += 45
            signals.append("TOR exit node detected")

        # VPN
        if is_vpn:
            score += 25
            signals.append("VPN connection detected")

        # Proxy
        if is_proxy:
            score += 20
            signals.append("Proxy server detected")

        # Datacenter IP
        if is_datacenter or self._is_datacenter_ip(ip_str):
            score += 20
            signals.append("Datacenter/cloud IP address")

        # Check for known suspicious patterns
        try:
            ip = ipaddress.ip_address(ip_str)
            # Private IP in production context
            if ip.is_private:
                score += 30
                signals.append("Private IP address in transaction")
            # Loopback
            if ip.is_loopback:
                score += 40
                signals.append("Loopback address detected")
        except ValueError:
            score += 10
            signals.append("Invalid IP address format")

        # Multiple risk indicators compound
        risk_count = sum([is_vpn, is_tor, is_proxy, is_datacenter])
        if risk_count >= 2:
            score += 15
            signals.append(f"Multiple IP risk indicators ({risk_count})")

        # IP mismatch with geo (if both available)
        ip_country = metadata.get("ip_country")
        geo_country = metadata.get("geo_country")
        if ip_country and geo_country and ip_country != geo_country:
            score += 15
            signals.append(f"IP country ({ip_country}) doesn't match geo ({geo_country})")

        confidence = 0.75

        return ScoringResult(
            score=min(100.0, score),
            confidence=confidence,
            signals=signals,
            metadata={"ip": ip_str, "is_vpn": is_vpn, "is_tor": is_tor},
        )

    def _is_datacenter_ip(self, ip: str) -> bool:
        """Simple heuristic check for datacenter IPs."""
        return any(ip.startswith(prefix) for prefix in DATACENTER_PREFIXES)
