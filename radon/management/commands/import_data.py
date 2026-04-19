"""
Import Ohio radon data from the MySQL SQL dump files in
/Users/wrwatkins/Dropbox/Code/radoninohio-com/assets/sql/ (or any directory
passed via --sql-dir).

Run order (dependencies enforced):
  1. ohcounties   → County
  2. ohzips       → ZipCode (linked to County by county_fips)
  3. census_zcta  → ZipCode.geometry (GeoJSON embedded in LONGBLOB column)
  4. ohcities     → City (linked to County by county_fips, ZIP M2M via `zips` col)
  5. radonlevels  → RadonLevel (linked to ZipCode + County)
  6. contractors  → Contractor (linked to County by county_fips)

Usage:
  python manage.py import_data
  python manage.py import_data --sql-dir /path/to/sql
  python manage.py import_data --only counties zips    # subset
"""

import json
import re
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from radon.models import City, Contractor, County, RadonLevel, ZipCode

# Local dev default; override with --sql-dir inside Docker
DEFAULT_SQL_DIR = Path("/Users/wrwatkins/Dropbox/Code/radoninohio-com/assets/sql")


# ── SQL parsing helpers ───────────────────────────────────────────────────────

def _parse_sql_rows(path: Path):
    """
    Yield (columns, values_list) from a phpMyAdmin-style MySQL dump.
    Handles multi-row INSERT … VALUES (…),(…) blocks.
    """
    text = path.read_text(encoding="utf-8", errors="replace")

    # Find INSERT INTO `table` (`col1`, …) VALUES
    insert_re = re.compile(
        r"INSERT INTO `\w+` \(([^)]+)\) VALUES\s*(.*?);\s*$",
        re.DOTALL | re.MULTILINE,
    )
    for m in insert_re.finditer(text):
        columns = [c.strip().strip("`") for c in m.group(1).split(",")]
        values_block = m.group(2)
        for row in _split_value_rows(values_block):
            yield columns, row


def _split_value_rows(values_block: str):
    """Split a VALUES block into individual row tuples, handling quoted strings."""
    rows = []
    depth = 0
    in_quote = False
    escape_next = False
    current = []
    buf = []

    for ch in values_block:
        if escape_next:
            buf.append(ch)
            escape_next = False
            continue
        if ch == "\\" and in_quote:
            buf.append(ch)
            escape_next = True
            continue
        if ch == "'" and not in_quote:
            in_quote = True
            buf.append(ch)
            continue
        if ch == "'" and in_quote:
            in_quote = False
            buf.append(ch)
            continue
        if in_quote:
            buf.append(ch)
            continue
        if ch == "(":
            if depth == 0:
                buf = []
            else:
                buf.append(ch)
            depth += 1
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                current.append("".join(buf).strip())
                rows.append(_parse_row(current))
                current = []
                buf = []
            else:
                buf.append(ch)
            continue
        if ch == "," and depth == 1:
            current.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)

    return rows


def _parse_row(raw_values):
    """Convert raw token strings to Python scalars."""
    result = []
    for val in raw_values:
        val = val.strip()
        if val.upper() == "NULL":
            result.append(None)
        elif val.startswith("'") and val.endswith("'"):
            inner = val[1:-1]
            inner = inner.replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
            result.append(inner)
        else:
            try:
                if "." in val:
                    result.append(float(val))
                else:
                    result.append(int(val))
            except (ValueError, TypeError):
                result.append(val)
    return result


def _row_to_dict(columns, row):
    return dict(zip(columns, row))


def _float_or_none(val):
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _int_or_none(val):
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


# ── Import routines ───────────────────────────────────────────────────────────

def import_counties(sql_dir: Path, stdout):
    """ohcounties → County"""
    path = sql_dir / "ohcounties.sql"
    if not path.exists():
        raise CommandError(f"Not found: {path}")

    created = updated = 0
    with transaction.atomic():
        County.objects.filter(state="OH").delete()
        rows = list(_parse_sql_rows(path))
        for columns, row in rows:
            d = _row_to_dict(columns, row)
            County.objects.create(
                name=str(d.get("county_name", "") or "").strip(),
                fips=str(d.get("fips", "") or ""),
                state=str(d.get("state", "OH") or "OH"),
                county_seat=str(d.get("county_seat", "") or ""),
            )
            created += 1

    stdout.write(f"  Counties: {created} created, {updated} updated")


def import_zips(sql_dir: Path, stdout):
    """ohzips → ZipCode (county FK by county_fips)"""
    path = sql_dir / "ohzips.sql"
    if not path.exists():
        raise CommandError(f"Not found: {path}")

    county_by_fips = {c.fips: c for c in County.objects.filter(state="OH") if c.fips}
    created = skipped = 0

    with transaction.atomic():
        ZipCode.objects.filter(state="OH").delete()
        for columns, row in _parse_sql_rows(path):
            d = _row_to_dict(columns, row)
            zip_val = str(d.get("zip", "") or "").strip().zfill(5)
            if not zip_val or len(zip_val) != 5:
                skipped += 1
                continue
            fips = str(d.get("county_fips", "") or "")
            county = county_by_fips.get(fips)
            ZipCode.objects.create(
                zip=zip_val,
                city=str(d.get("city", "") or ""),
                county=county,
                state=str(d.get("state_id", "OH") or "OH"),
                lat=_float_or_none(d.get("lat")),
                lng=_float_or_none(d.get("lng")),
                population=_float_or_none(d.get("population")),
                density=_float_or_none(d.get("density")),
                timezone=str(d.get("timezone", "") or ""),
            )
            created += 1

    stdout.write(f"  ZIPs: {created} created, {skipped} skipped")


def import_zcta_geometry(sql_dir: Path, stdout):
    """census_zcta → ZipCode.geometry (GeoJSON fragment stored as string)"""
    path = sql_dir / "census_zcta.sql"
    if not path.exists():
        raise CommandError(f"Not found: {path}")

    zip_map = {z.zip: z for z in ZipCode.objects.filter(state="OH")}
    updated = skipped = errors = 0

    for columns, row in _parse_sql_rows(path):
        d = _row_to_dict(columns, row)
        zcta = str(d.get("zcta", "") or "").strip().zfill(5)
        geo_str = d.get("geo")
        if not geo_str or zcta not in zip_map:
            skipped += 1
            continue
        try:
            # geo column contains partial GeoJSON: '"geometry": { "type": "...", "coordinates": [...] }'
            # Wrap it in a full GeoJSON object
            geojson_str = "{" + str(geo_str) + "}"
            geojson = json.loads(geojson_str)
            geom_dict = geojson.get("geometry") or geojson
            geom = GEOSGeometry(json.dumps(geom_dict), srid=4326)
            if geom.geom_type == "Polygon":
                geom = MultiPolygon(geom, srid=4326)
            land = _int_or_none(d.get("land"))
            water = _int_or_none(d.get("water"))
            ZipCode.objects.filter(zip=zcta).update(
                geometry=geom,
                land_area=land,
                water_area=water,
            )
            updated += 1
        except Exception:
            errors += 1

    stdout.write(f"  ZCTA geometry: {updated} updated, {skipped} skipped, {errors} errors")


def import_cities(sql_dir: Path, stdout):
    """ohcities → City (M2M ZipCode via `zips` space-separated column)"""
    path = sql_dir / "ohcities.sql"
    if not path.exists():
        raise CommandError(f"Not found: {path}")

    county_by_fips = {c.fips: c for c in County.objects.filter(state="OH") if c.fips}
    zip_map = {z.zip: z for z in ZipCode.objects.filter(state="OH")}
    created = skipped = 0

    with transaction.atomic():
        City.objects.filter(state="OH").delete()

    city_zip_pairs = []
    for columns, row in _parse_sql_rows(path):
        d = _row_to_dict(columns, row)
        state_id = str(d.get("state_id", "") or "").strip()
        if state_id != "OH":
            continue
        fips = str(d.get("county_fips", "") or "")
        county = county_by_fips.get(fips)
        zips_raw = str(d.get("zips", "") or "")
        zip_list = [z.strip().zfill(5) for z in zips_raw.split() if z.strip()]

        city = None
        try:
            with transaction.atomic():
                city = City.objects.create(
                    name=str(d.get("city", "") or "").strip(),
                    name_ascii=str(d.get("city_ascii", "") or "").strip(),
                    state="OH",
                    county=county,
                    lat=_float_or_none(d.get("lat")),
                    lng=_float_or_none(d.get("lng")),
                    population=_float_or_none(d.get("population")),
                    density=_float_or_none(d.get("density")),
                    timezone=str(d.get("timezone", "") or ""),
                    ranking=_int_or_none(d.get("ranking")),
                )
            created += 1
        except Exception:
            skipped += 1
        if city:
            city_zip_pairs.append((city, zip_list))

    # Wire M2M (must be outside the delete transaction to avoid FK issues)
    for city, zip_list in city_zip_pairs:
        zip_objs = [zip_map[z] for z in zip_list if z in zip_map]
        if zip_objs:
            city.zip_codes.set(zip_objs)

    stdout.write(f"  Cities: {created} created, {skipped} skipped")


def _safe_create(create_fn):
    """
    Wrap a single ORM create in a savepoint so that a Postgres error on one row
    doesn't abort the enclosing transaction (unlike MySQL, PG marks the whole
    transaction aborted after any statement error, even if caught by Python).
    """
    try:
        with transaction.atomic():
            create_fn()
            return True
    except Exception:
        return False


def import_radon_levels(sql_dir: Path, stdout):
    """radonlevels → RadonLevel (linked to ZipCode + County)"""
    path = sql_dir / "radonlevels.sql"
    if not path.exists():
        raise CommandError(f"Not found: {path}")

    zip_map = {z.zip: z for z in ZipCode.objects.filter(state="OH")}
    county_by_fips = {c.fips: c for c in County.objects.filter(state="OH") if c.fips}
    county_by_name = {c.name.lower(): c for c in County.objects.filter(state="OH")}
    created = skipped = 0

    with transaction.atomic():
        RadonLevel.objects.all().delete()

    for columns, row in _parse_sql_rows(path):
        d = _row_to_dict(columns, row)
        zip_val = str(d.get("zip", "") or "").strip().zfill(5)
        fips = str(d.get("fips", "") or "")
        county_name_raw = str(d.get("county_name", "") or "").lower()

        zip_obj = zip_map.get(zip_val) if zip_val and zip_val != "00000" else None
        county_obj = county_by_fips.get(fips) or county_by_name.get(county_name_raw)

        if not zip_obj and not county_obj:
            skipped += 1
            continue

        ok = _safe_create(lambda: RadonLevel.objects.create(
            zip_code=zip_obj,
            county=county_obj if not zip_obj else None,
            state=str(d.get("state", "OH") or "OH"),
            testcount=int(d.get("testcount") or 0),
            testmin=float(d.get("testmin") or 0),
            testmax=float(d.get("testmax") or 0),
            testmean=float(d.get("testmean") or 0),
            teststdev=_float_or_none(d.get("teststdev")),
            testgeomean=_float_or_none(d.get("testgeomean")),
            usepa_radon_zone=_int_or_none(d.get("usepa_radon_zone")),
            publisher=str(d.get("publisher", "") or ""),
            pubdate=d.get("pubdate") or None,
            pubsource=str(d.get("pubsource", "") or ""),
            pub_represents_period=str(d.get("pub_represents_period", "") or ""),
        ))
        if ok:
            created += 1
        else:
            skipped += 1

    stdout.write(f"  RadonLevels: {created} created, {skipped} skipped")


def import_contractors(sql_dir: Path, stdout):
    """contractors → Contractor"""
    path = sql_dir / "contractors.sql"
    if not path.exists():
        raise CommandError(f"Not found: {path}")

    county_by_fips = {c.fips: c for c in County.objects.filter(state="OH") if c.fips}
    county_by_name = {c.name.lower(): c for c in County.objects.filter(state="OH")}

    TYPE_MAP = {
        "tester": Contractor.TESTER,
        "mitigator": Contractor.MITIGATOR,
        "both": Contractor.BOTH,
        "mitigator/tester": Contractor.BOTH,
        "tester/mitigator": Contractor.BOTH,
        # actual values from Ohio Dept of Health export:
        "radon tester": Contractor.TESTER,
        "radon contractor": Contractor.MITIGATOR,
        "radon specialist": Contractor.BOTH,
    }
    created = skipped = 0

    with transaction.atomic():
        Contractor.objects.all().delete()

    for columns, row in _parse_sql_rows(path):
        d = _row_to_dict(columns, row)
        license_val = str(d.get("license", "") or "").strip()
        if not license_val:
            skipped += 1
            continue
        raw_type = str(d.get("type", "") or "").strip().lower()
        contractor_type = TYPE_MAP.get(raw_type, Contractor.BOTH)
        fips = str(d.get("county_fips", "") or "")
        county_name_raw = str(d.get("county_name", "") or "").lower()
        county = county_by_fips.get(fips) or county_by_name.get(county_name_raw)

        ok = _safe_create(lambda: Contractor.objects.create(
            contractor_type=contractor_type,
            license=license_val,
            name=str(d.get("name", "") or ""),
            business=str(d.get("business", "") or ""),
            address1=str(d.get("address1", "") or ""),
            address2=str(d.get("address2", "") or ""),
            city=str(d.get("city", "") or ""),
            state=str(d.get("state", "OH") or "OH"),
            zip=str(d.get("zip", "") or ""),
            county=county,
            phone=str(d.get("phone", "") or ""),
            website=str(d.get("urlwebsite", "") or ""),
            lat=_float_or_none(d.get("lat")),
            lng=_float_or_none(d.get("lng")),
        ))
        if ok:
            created += 1
        else:
            skipped += 1

    stdout.write(f"  Contractors: {created} created, {skipped} skipped")


# ── Management command ────────────────────────────────────────────────────────

STEPS = {
    "counties": import_counties,
    "zips": import_zips,
    "geometry": import_zcta_geometry,
    "cities": import_cities,
    "radon": import_radon_levels,
    "contractors": import_contractors,
}

STEP_ORDER = ["counties", "zips", "geometry", "cities", "radon", "contractors"]


class Command(BaseCommand):
    help = "Import Ohio radon data from MySQL SQL dump files into PostGIS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sql-dir",
            type=Path,
            default=DEFAULT_SQL_DIR,
            help="Directory containing the SQL dump files (default: %(default)s)",
        )
        parser.add_argument(
            "--only",
            nargs="+",
            choices=list(STEPS.keys()),
            metavar="STEP",
            help=f"Run only these steps: {', '.join(STEPS.keys())}",
        )

    def handle(self, *args, **options):
        sql_dir = options["sql_dir"]
        if not sql_dir.exists():
            raise CommandError(f"SQL directory not found: {sql_dir}")

        steps = options["only"] or STEP_ORDER
        # Preserve dependency order even if user passes --only
        steps = [s for s in STEP_ORDER if s in steps]

        self.stdout.write(self.style.SUCCESS(f"Importing from {sql_dir}"))
        for step in steps:
            self.stdout.write(f"→ {step}")
            STEPS[step](sql_dir, self.stdout)

        self.stdout.write(self.style.SUCCESS("Import complete."))
