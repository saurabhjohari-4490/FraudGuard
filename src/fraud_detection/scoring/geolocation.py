"""Geolocation Engine - detects impossible travel and geo anomalies. Weight: 10%."""

import math

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers."""
    R = 6371  # Earth radius in km
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


class GeolocationEngine(ScoringModule):
    name = "geolocation"
    weight = 0.10
    description = "Detects impossible travel and geolocation anomalies"

    # Thresholds
    IMPOSSIBLE_TRAVEL_SPEED_KPH = 900  # Faster than commercial aviation
    SUSPICIOUS_TRAVEL_SPEED_KPH = 500  # Fast but possible
    HIGH_RISK_DISTANCE_KM = 1000

    async def score(self, context: TransactionContext) -> ScoringResult:
        signals: list[str] = []
        score = 0.0

        if context.geo_lat is None or context.geo_lon is None:
            # No geolocation data
            return ScoringResult(score=0, confidence=0.2, signals=["No geolocation data"])

        # Check if user has typical geo regions
        enrichment = context.enrichment
        if enrichment.user_typical_geo_regions:
            # Simple check: is current location in a known region?
            current_region = self._get_region(context.geo_lat, context.geo_lon)
            if current_region and current_region not in enrichment.user_typical_geo_regions:
                score += 25
                signals.append(f"Transaction from new geographic region: {current_region}")

        # Check for impossible travel using metadata
        last_lat = context.metadata.get("last_geo_lat")
        last_lon = context.metadata.get("last_geo_lon")
        last_time = context.metadata.get("last_txn_time")

        if last_lat is not None and last_lon is not None and last_time is not None:
            distance_km = haversine_distance_km(
                last_lat, last_lon, context.geo_lat, context.geo_lon
            )
            time_diff_hours = (context.timestamp.timestamp() - last_time) / 3600

            if time_diff_hours > 0 and distance_km > 50:
                speed_kph = distance_km / time_diff_hours

                if speed_kph > self.IMPOSSIBLE_TRAVEL_SPEED_KPH:
                    score += 60
                    signals.append(
                        f"Impossible travel: {distance_km:.0f}km in {time_diff_hours*60:.0f}min "
                        f"({speed_kph:.0f} km/h)"
                    )
                elif speed_kph > self.SUSPICIOUS_TRAVEL_SPEED_KPH:
                    score += 30
                    signals.append(
                        f"Suspicious travel speed: {distance_km:.0f}km in {time_diff_hours*60:.0f}min"
                    )

            if distance_km > self.HIGH_RISK_DISTANCE_KM:
                score += 15
                signals.append(f"Large geographic displacement: {distance_km:.0f}km from last transaction")

        # High-risk countries/regions
        risk_region = context.metadata.get("geo_risk_region")
        if risk_region:
            score += 20
            signals.append(f"Transaction from high-risk region: {risk_region}")

        confidence = 0.8 if (context.geo_lat and context.geo_lon) else 0.3

        return ScoringResult(
            score=min(100.0, score),
            confidence=confidence,
            signals=signals,
            metadata={"lat": context.geo_lat, "lon": context.geo_lon},
        )

    def _get_region(self, lat: float, lon: float) -> str:
        """Simplified region detection based on coordinates."""
        if 8 <= lat <= 37 and 68 <= lon <= 97:
            return "IN"  # India
        elif 25 <= lat <= 50 and -125 <= lon <= -65:
            return "US"
        elif 35 <= lat <= 72 and -10 <= lon <= 40:
            return "EU"
        elif 20 <= lat <= 45 and 100 <= lon <= 145:
            return "APAC"
        return "OTHER"
