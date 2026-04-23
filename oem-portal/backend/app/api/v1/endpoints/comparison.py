from fastapi import APIRouter, Query
from typing import List
from app.data.seed import COMPONENTS, PARAMETERS

router = APIRouter(prefix="/comparison")


@router.get("/matrix")
async def comparison_matrix(model_ids: str = Query(..., description="Comma-separated component IDs")):
    ids = [mid.strip() for mid in model_ids.split(",") if mid.strip()]
    models = [c for c in COMPONENTS if c["id"] in ids]

    if not models:
        return {"models": [], "rows": []}

    # Collect all param codes across selected models
    all_codes = set()
    model_params = {}
    for m in models:
        params = PARAMETERS.get(m["id"], [])
        model_params[m["id"]] = {p["code"]: p for p in params}
        for p in params:
            all_codes.add((p["code"], p["name"], p["unit"], p["section"]))

    # Sort by section then name
    sorted_codes = sorted(all_codes, key=lambda x: (x[3], x[1]))

    rows = []
    for code, name, unit, section in sorted_codes:
        row = {
            "code": code,
            "parameter": name,
            "unit": unit,
            "section": section,
            "values": {},
        }
        values_numeric = []
        for m in models:
            p = model_params.get(m["id"], {}).get(code)
            if p:
                row["values"][m["id"]] = {
                    "value": p["value"],
                    "verified": p.get("verified", True),
                    "display": f"{p['value']} {p['unit']}".strip(),
                }
                try:
                    values_numeric.append(float(p["value"]))
                except (ValueError, TypeError):
                    pass
            else:
                row["values"][m["id"]] = {"value": None, "verified": False, "display": "—"}

        # Determine best/worst for numeric values
        if len(values_numeric) >= 2:
            row["benchmark"] = {
                "min": min(values_numeric),
                "max": max(values_numeric),
                "avg": round(sum(values_numeric) / len(values_numeric), 2),
            }

        rows.append(row)

    return {
        "models": [{"id": m["id"], "model_name": m["model_name"], "oem_name": m["oem_name"], "score": m.get("compliance_score", 0)} for m in models],
        "rows": rows,
        "total_parameters": len(rows),
    }
