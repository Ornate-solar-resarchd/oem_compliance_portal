from fastapi import APIRouter
from app.data.seed import OEMS, COMPONENTS, PROJECTS, SHEETS, WORKFLOWS, PARAMETERS

router = APIRouter(prefix="/dashboard")


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
        model_scores = [{"model": m["model_name"], "score": m["compliance_score"]} for m in oem_models]
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
            sections[sec].append({"name": p["name"], "value": p["value"], "unit": p["unit"], "status": p["status"]})

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
            "compliance_score": comp["compliance_score"],
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
