from fastapi import APIRouter
from app.data.seed import OEMS, COMPONENTS, PROJECTS, SHEETS, WORKFLOWS, PARAMETERS
from app.api.v1.completeness import completeness as _completeness

router = APIRouter(prefix="/dashboard")


@router.get("/summary")
async def dashboard_summary():
    """All data needed for the new dashboard in one call."""

    # ── Category breakdown ──────────────────────────────────────────
    categories = ["Cell", "PCS", "EMS", "DC Block"]
    category_counts = {cat: 0 for cat in categories}
    for c in COMPONENTS:
        cat = c.get("component_type_name", "")
        if cat in category_counts:
            category_counts[cat] += 1

    # ── OEM summary ─────────────────────────────────────────────────
    oem_rows = []
    for oem in OEMS:
        oem_comps = [c for c in COMPONENTS if c.get("oem_id") == oem["id"]]
        scores = [_completeness(c) for c in oem_comps]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        cats = list({c.get("component_type_name", "") for c in oem_comps})
        oem_rows.append({
            "id": oem["id"],
            "name": oem["name"],
            "model_count": len(oem_comps),
            "avg_completeness": avg,
            "categories": cats,
            "is_approved": oem.get("is_approved", False),
        })

    # Sort: most models first
    oem_rows.sort(key=lambda x: x["model_count"], reverse=True)

    # ── Data coverage ────────────────────────────────────────────────
    coverage = []
    for c in COMPONENTS:
        score = _completeness(c)
        coverage.append({
            "id": c["id"],
            "oem_name": c.get("oem_name", ""),
            "model_name": c.get("model_name", ""),
            "category": c.get("component_type_name", ""),
            "completeness": score,
            "parameters_count": len(PARAMETERS.get(c["id"], [])),
            "has_datasheet": bool(c.get("datasheet") or c.get("gdrive_file_id")),
        })

    # Sort: lowest completeness first (needs attention)
    coverage.sort(key=lambda x: x["completeness"])

    # ── Recent imports ───────────────────────────────────────────────
    # Components added via upload/gdrive have comp-upload / comp-gdrive / comp-batch prefixes
    recent = [c for c in COMPONENTS if any(
        c["id"].startswith(p) for p in ("comp-upload", "comp-gdrive", "comp-batch", "comp-slack")
    )]
    recent_out = [{
        "id": c["id"],
        "oem_name": c.get("oem_name", ""),
        "model_name": c.get("model_name", ""),
        "category": c.get("component_type_name", ""),
        "source": c.get("source", "upload"),
        "datasheet": c.get("datasheet", ""),
        "completeness": _completeness(c),
    } for c in recent[-10:][::-1]]  # last 10, newest first

    # ── Totals ───────────────────────────────────────────────────────
    all_scores = [_completeness(c) for c in COMPONENTS]
    avg_completeness = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    return {
        "totals": {
            "oems": len(OEMS),
            "models": len(COMPONENTS),
            "avg_completeness": avg_completeness,
            "approved_oems": sum(1 for o in OEMS if o.get("is_approved")),
        },
        "category_breakdown": [
            {"category": cat, "count": category_counts[cat]}
            for cat in categories
        ],
        "oem_summary": oem_rows,
        "data_coverage": coverage,
        "recent_imports": recent_out,
    }


@router.get("/stats")
async def dashboard_stats():
    active_projects = len([p for p in PROJECTS if p["status"] == "active"])
    sheets_in_review = len([s for s in SHEETS if s["workflow_stage"] not in ("draft", "locked")])
    pending_approvals = len(WORKFLOWS)
    scores = [s["compliance_score"] for s in SHEETS if s["compliance_score"]]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    return {
        "active_projects": active_projects,
        "sheets_in_review": sheets_in_review,
        "pending_approvals": pending_approvals,
        "avg_compliance_score": avg_score,
    }


@router.get("/charts/{entity_id}")
async def dashboard_charts(entity_id: str):
    # If entity_id is an OEM id, return model scores for that OEM
    oem = next((o for o in OEMS if o["id"] == entity_id), None)
    if oem:
        oem_models = [c for c in COMPONENTS if c["oem_id"] == entity_id]
        model_scores = [{"model": m["model_name"], "score": m.get("compliance_score", 0)} for m in oem_models]
        # Build parameter chart data from first model
        param_chart = []
        if oem_models:
            params = PARAMETERS.get(oem_models[0]["id"], [])
            if params:
                for p in params:
                    if p["section"] == "Electrical" and p["value"]:
                        try:
                            param_chart.append({"name": p["name"], "value": float(p["value"]), "unit": p["unit"]})
                        except ValueError:
                            pass
        return {
            "oem_name": oem["name"],
            "model_scores": model_scores,
            "electrical_params": param_chart,
            "compliance_breakdown": {
                "pass": sum(m.get("pass", 0) for m in oem_models),
                "fail": sum(m.get("fail", 0) for m in oem_models),
                "waived": sum(m.get("waived", 0) for m in oem_models),
            }
        }

    # If entity_id is a component id, return parameter data
    comp = next((c for c in COMPONENTS if c["id"] == entity_id), None)
    if comp:
        params = PARAMETERS.get(entity_id, [])
        sections = {}
        for p in params:
            sec = p.get("section", "Other")
            if sec not in sections:
                sections[sec] = []
            sections[sec].append({"name": p["name"], "value": p["value"], "unit": p["unit"], "verified": p.get("verified", True)})

        electrical = [p for p in params if p["section"] == "Electrical" and p["value"]]
        chart_data = []
        for p in electrical:
            try:
                chart_data.append({"name": p["name"], "value": float(p["value"]), "unit": p["unit"]})
            except ValueError:
                pass

        return {
            "model_name": comp["model_name"],
            "oem_name": comp["oem_name"],
            "sections": sections,
            "electrical_chart": chart_data,
            "compliance_score": comp.get("compliance_score", 0),
        }

    return {"error": "Entity not found"}


@router.get("/overview")
async def dashboard_overview():
    return {
        "oems": len(OEMS),
        "components": len(COMPONENTS),
        "projects": len(PROJECTS),
        "sheets": len(SHEETS),
        "locked": len([s for s in SHEETS if s["workflow_stage"] == "locked"]),
    }
