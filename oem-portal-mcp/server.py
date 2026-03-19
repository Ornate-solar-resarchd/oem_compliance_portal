#!/usr/bin/env python3
"""
MCP Server for UnityESS OEM Portal.

Connects Claude to the UnityESS Technical Compliance Portal backend API,
enabling direct queries for OEMs, components, parameters, RFQ matching,
comparison matrices, workflow management, and technical mail.
"""

import json
import os
from typing import Optional, List, Dict, Any
from enum import Enum

import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# ── Server Init ──────────────────────────────────────────────────────────────

mcp = FastMCP("oem_portal_mcp")

API_BASE_URL = os.environ.get("OEM_PORTAL_URL", "http://localhost:8000/api/v1")
REQUEST_TIMEOUT = 30.0


# ── Shared Utilities ─────────────────────────────────────────────────────────

async def _api(endpoint: str, method: str = "GET", **kwargs) -> dict:
    """Reusable API request function for all OEM Portal calls."""
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json()


def _err(e: Exception) -> str:
    """Consistent error formatting."""
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        if code == 404:
            return "Error: Resource not found. Check the ID and try again."
        if code == 422:
            return f"Error: Validation failed. {e.response.text}"
        return f"Error: API returned HTTP {code}."
    if isinstance(e, httpx.ConnectError):
        return "Error: Cannot reach OEM Portal backend. Is it running on localhost:8000?"
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again."
    return f"Error: {type(e).__name__}: {e}"


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


def _fmt_table(rows: List[Dict], cols: List[str], headers: Optional[List[str]] = None) -> str:
    """Format a list of dicts as a Markdown table."""
    hdrs = headers or cols
    lines = ["| " + " | ".join(hdrs) + " |"]
    lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for r in rows:
        vals = [str(r.get(c, "—")) for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


# ── Input Models ─────────────────────────────────────────────────────────────

class OEMListInput(BaseModel):
    """Input for listing OEMs."""
    model_config = ConfigDict(str_strip_whitespace=True)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class OEMDetailInput(BaseModel):
    """Input for getting a single OEM with its models."""
    model_config = ConfigDict(str_strip_whitespace=True)
    oem_id: str = Field(..., description="OEM ID (e.g. 'oem-catl-001')", min_length=1)


class ComponentListInput(BaseModel):
    """Input for listing component models."""
    model_config = ConfigDict(str_strip_whitespace=True)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ComponentParamsInput(BaseModel):
    """Input for getting parameters of a component model."""
    model_config = ConfigDict(str_strip_whitespace=True)
    component_id: str = Field(..., description="Component model ID (e.g. 'comp-catl-280')", min_length=1)
    section: Optional[str] = Field(
        default=None,
        description="Filter by section: 'Electrical', 'Physical', 'Thermal', 'Safety', 'Performance'",
    )


class ComparisonInput(BaseModel):
    """Input for comparing OEM models side by side."""
    model_config = ConfigDict(str_strip_whitespace=True)
    model_ids: List[str] = Field(
        ...,
        description="List of component model IDs to compare (e.g. ['comp-catl-280', 'comp-byd-blade'])",
        min_length=2,
    )


class RFQMatchInput(BaseModel):
    """Input for matching an RFQ against all OEM models."""
    model_config = ConfigDict(str_strip_whitespace=True)
    rfq_id: str = Field(..., description="RFQ ID (e.g. 'rfq-001')", min_length=1)


class WorkflowAdvanceInput(BaseModel):
    """Input for advancing a sheet's workflow stage."""
    model_config = ConfigDict(str_strip_whitespace=True)
    sheet_id: str = Field(..., description="Sheet ID (e.g. 'sheet-001')", min_length=1)
    action: str = Field(
        ...,
        description="Workflow action: 'approve', 'reject', 'submit', or 'sign'",
    )
    comment: Optional[str] = Field(default=None, description="Review comment (required for reject)")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        allowed = {"approve", "reject", "submit", "sign"}
        if v.lower() not in allowed:
            raise ValueError(f"Action must be one of: {', '.join(allowed)}")
        return v.lower()


class TechnicalMailInput(BaseModel):
    """Input for sending a technical data email."""
    model_config = ConfigDict(str_strip_whitespace=True)
    to: str = Field(..., description="Recipient email address", min_length=3)
    component_id: str = Field(..., description="Component model ID whose data to send", min_length=1)
    subject: Optional[str] = Field(default=None, description="Email subject (auto-generated if omitted)")
    sections: Optional[List[str]] = Field(
        default=None,
        description="Parameter sections to include: ['Electrical', 'Physical', 'Thermal', 'Safety', 'Performance']",
    )


class DashboardInput(BaseModel):
    """Input for dashboard data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# ── Tools ────────────────────────────────────────────────────────────────────

@mcp.tool(
    name="oem_portal_list_oems",
    annotations={
        "title": "List All OEMs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_list_oems(params: OEMListInput) -> str:
    """List all OEM manufacturers in the UnityESS portal with their compliance scores, model counts, and approval status.

    Returns CATL, Lishen, BYD, HiTHIUM and any other registered OEMs.

    Args:
        params: response_format — 'markdown' (default) or 'json'

    Returns:
        Table of OEMs with name, country, score, model count, approved status.
    """
    try:
        data = await _api("oems/")
        oems = data.get("items", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        lines = [f"# OEM Library — {len(oems)} Manufacturers\n"]
        for o in oems:
            status = "Approved" if o.get("is_approved") else "Pending"
            lines.append(f"**{o['name']}** ({o.get('country_of_origin', '—')}) — Score: {o.get('score', '—')} — {o.get('models', 0)} models — {status}")
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_get_oem",
    annotations={
        "title": "Get OEM Detail",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_get_oem(params: OEMDetailInput) -> str:
    """Get detailed information about a specific OEM including all their component models.

    Args:
        params: oem_id — the OEM's unique ID (e.g. 'oem-catl-001')

    Returns:
        OEM details with list of component models, compliance scores, and fill rates.
    """
    try:
        data = await _api(f"oems/{params.oem_id}")
        if "error" in data:
            return f"Error: {data['error']}"

        models = data.get("models", [])
        lines = [
            f"# {data['name']}",
            f"Country: {data.get('country_of_origin', '—')} | Score: {data.get('score', '—')} | Approved: {'Yes' if data.get('is_approved') else 'No'}",
            "",
            f"## Component Models ({len(models)})\n",
        ]
        if models:
            lines.append(_fmt_table(
                models,
                ["model_name", "component_type_name", "compliance_score", "fill_rate", "is_active"],
                ["Model", "Type", "Score", "Fill %", "Active"],
            ))
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_list_components",
    annotations={
        "title": "List Component Models",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_list_components(params: ComponentListInput) -> str:
    """List all component models across all OEMs with compliance scores.

    Returns battery cell models from CATL, Lishen, BYD, HiTHIUM etc.

    Args:
        params: response_format — 'markdown' or 'json'

    Returns:
        Table of components with model name, OEM, type, score, fill rate.
    """
    try:
        data = await _api("components/")
        items = data.get("items", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        lines = [f"# Component Models — {len(items)} Total\n"]
        lines.append(_fmt_table(
            items,
            ["model_name", "oem_name", "component_type_name", "compliance_score", "fill_rate"],
            ["Model", "OEM", "Type", "Score", "Fill %"],
        ))
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_get_parameters",
    annotations={
        "title": "Get Component Parameters",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_get_parameters(params: ComponentParamsInput) -> str:
    """Get all technical parameters for a specific component model, with values, units, and compliance status.

    Returns 28 parameters grouped by section: Electrical, Physical, Thermal, Safety, Performance.

    Args:
        params: component_id — e.g. 'comp-catl-280'. Optional section filter.

    Returns:
        Parameter list with name, value, unit, section, pass/fail status, AI confidence.
    """
    try:
        data = await _api(f"components/{params.component_id}/parameters")
        items = data.get("items", [])

        if params.section:
            items = [p for p in items if p.get("section", "").lower() == params.section.lower()]

        if not items:
            return f"No parameters found for component '{params.component_id}'" + (f" in section '{params.section}'" if params.section else "")

        # Group by section
        sections: Dict[str, list] = {}
        for p in items:
            sec = p.get("section", "Other")
            sections.setdefault(sec, []).append(p)

        lines = [f"# Parameters for {params.component_id}\n"]
        for sec_name, sec_params in sections.items():
            lines.append(f"## {sec_name}\n")
            lines.append(_fmt_table(
                sec_params,
                ["name", "value", "unit", "status", "confidence"],
                ["Parameter", "Value", "Unit", "Status", "AI Conf."],
            ))
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_compare_models",
    annotations={
        "title": "Compare Component Models",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_compare_models(params: ComparisonInput) -> str:
    """Compare multiple OEM component models side by side across all parameters.

    Shows parameter values for each model with pass/fail status and benchmarks (min/max/avg).

    Args:
        params: model_ids — list of 2+ component IDs to compare

    Returns:
        Comparison matrix with models as columns and parameters as rows.
    """
    try:
        ids_str = ",".join(params.model_ids)
        data = await _api(f"comparison/matrix?model_ids={ids_str}")
        models = data.get("models", [])
        rows = data.get("rows", [])

        if not models:
            return "No models found for the given IDs."

        model_names = [f"{m['oem_name']} {m['model_name']}" for m in models]

        lines = [
            f"# Comparison — {len(models)} Models, {len(rows)} Parameters\n",
            "## Compliance Scores\n",
        ]
        for m in models:
            lines.append(f"- **{m['oem_name']} {m['model_name']}**: {m['score']}%")
        lines.append("")

        # Build table
        header = ["Parameter", "Unit"] + [m["oem_name"] for m in models]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")

        current_section = ""
        for row in rows:
            sec = row.get("section", "")
            if sec != current_section:
                current_section = sec
                lines.append(f"| **{sec}** | | " + " | ".join([""] * len(models)) + " |")

            vals = []
            for m in models:
                v = row.get("values", {}).get(m["id"], {})
                disp = v.get("display", "—")
                status = v.get("status", "")
                marker = "P" if status == "pass" else ("F" if status == "fail" else "")
                vals.append(f"{disp} {marker}".strip())

            lines.append(f"| {row['parameter']} | {row.get('unit', '')} | " + " | ".join(vals) + " |")

        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_match_rfq",
    annotations={
        "title": "Match RFQ Against OEMs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_match_rfq(params: RFQMatchInput) -> str:
    """Match a customer RFQ against all OEM component models and rank by match percentage.

    Each requirement is checked parameter-by-parameter against every OEM model's data.

    Args:
        params: rfq_id — e.g. 'rfq-001'

    Returns:
        Ranked list of OEM models with match %, per-parameter pass/fail breakdown.
    """
    try:
        data = await _api(f"rfq/{params.rfq_id}/match")
        if "error" in data:
            return f"Error: {data['error']}"

        matches = data.get("matches", [])
        lines = [
            f"# RFQ Match Results — {data.get('customer', '?')}\n",
            f"Matched against {len(matches)} OEM models:\n",
        ]

        for i, m in enumerate(matches, 1):
            icon = "+++" if m["match_percentage"] >= 90 else ("++" if m["match_percentage"] >= 75 else "+")
            lines.append(f"## {i}. {m['oem_name']} — {m['model_name']} ({m['match_percentage']}%) {icon}")
            lines.append(f"Passed {m['passed']}/{m['total']} requirements\n")

            for d in m.get("details", []):
                status = "PASS" if d["match"] else "FAIL"
                lines.append(f"- {d['parameter']}: Required {d['required']} | OEM: {d['oem_value']} — **{status}**")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_list_rfqs",
    annotations={
        "title": "List RFQs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_list_rfqs(params: DashboardInput) -> str:
    """List all customer RFQs (Request for Quotation) in the system.

    Args:
        params: response_format — 'markdown' or 'json'

    Returns:
        List of RFQs with customer name, project, status, and requirement count.
    """
    try:
        data = await _api("rfq/")
        items = data.get("items", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        lines = [f"# RFQs — {len(items)} Total\n"]
        for r in items:
            reqs = len(r.get("requirements", []))
            lines.append(f"- **{r['id']}**: {r['customer_name']} — {r['project_name']} — {reqs} requirements — {r.get('status', '?')}")
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_dashboard",
    annotations={
        "title": "Dashboard Stats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_dashboard(params: DashboardInput) -> str:
    """Get portal dashboard KPIs: active projects, sheets in review, pending approvals, avg compliance score.

    Args:
        params: response_format — 'markdown' or 'json'

    Returns:
        Dashboard statistics summary.
    """
    try:
        data = await _api("dashboard/stats")

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        return (
            f"# OEM Portal Dashboard\n\n"
            f"- Active Projects: **{data['active_projects']}**\n"
            f"- Sheets In Review: **{data['sheets_in_review']}**\n"
            f"- Pending Approvals: **{data['pending_approvals']}**\n"
            f"- Avg Compliance Score: **{data['avg_compliance_score']}%**"
        )

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_pending_workflows",
    annotations={
        "title": "Pending Workflow Items",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_pending_workflows(params: DashboardInput) -> str:
    """List all technical sheets pending approval in the workflow pipeline.

    Args:
        params: response_format — 'markdown' or 'json'

    Returns:
        Table of pending sheets with sheet number, project, stage, score, waiting hours.
    """
    try:
        data = await _api("workflow/pending")
        items = data.get("items", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        lines = [f"# Pending Approvals — {len(items)} Sheets\n"]
        lines.append(_fmt_table(
            items,
            ["sheet_number", "project_name", "component_model_name", "workflow_stage", "compliance_score", "waiting_hours"],
            ["Sheet", "Project", "Model", "Stage", "Score", "Waiting (hrs)"],
        ))
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_advance_workflow",
    annotations={
        "title": "Advance Workflow",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def oem_portal_advance_workflow(params: WorkflowAdvanceInput) -> str:
    """Advance a technical sheet through the approval workflow (approve, reject, submit, or sign).

    Args:
        params: sheet_id, action ('approve'/'reject'/'submit'/'sign'), optional comment

    Returns:
        Confirmation with previous and new workflow stage.
    """
    try:
        body = {"action": params.action}
        if params.comment:
            body["comment"] = params.comment

        data = await _api(
            f"workflow/{params.sheet_id}/advance",
            method="POST",
            json=body,
        )
        if data.get("status") == "ok":
            return (
                f"Workflow advanced for sheet {params.sheet_id}:\n"
                f"- Action: {data.get('action', '?')}\n"
                f"- Previous stage: {data.get('previous_stage', '?')}\n"
                f"- New stage: {data.get('current_stage', '?')}"
            )
        return json.dumps(data, indent=2)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_send_technical_mail",
    annotations={
        "title": "Send Technical Mail",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def oem_portal_send_technical_mail(params: TechnicalMailInput) -> str:
    """Send technical data for a component model to a specified email address.

    Args:
        params: to (email), component_id, optional subject, optional sections filter

    Returns:
        Confirmation of email sent with parameter count included.
    """
    try:
        body: Dict[str, Any] = {
            "to": params.to,
            "component_id": params.component_id,
        }
        if params.subject:
            body["subject"] = params.subject
        if params.sections:
            body["sections"] = params.sections

        data = await _api("mail/technical", method="POST", json=body)
        return (
            f"Technical mail sent:\n"
            f"- To: {data.get('to', '?')}\n"
            f"- Subject: {data.get('subject', '?')}\n"
            f"- Model: {data.get('model_name', '?')} ({data.get('oem_name', '?')})\n"
            f"- Parameters included: {data.get('parameters_included', '?')}"
        )

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_list_projects",
    annotations={
        "title": "List Projects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_list_projects(params: DashboardInput) -> str:
    """List all BESS projects tracked in the portal with progress and capacity.

    Args:
        params: response_format — 'markdown' or 'json'

    Returns:
        Project list with name, client, type, capacity, location, progress.
    """
    try:
        data = await _api("projects/")
        items = data.get("items", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        lines = [f"# Projects — {len(items)} Total\n"]
        for p in items:
            kwh = f"{p.get('kwh', 0):,} kWh"
            lines.append(f"- **{p['name']}** — {p.get('client_name', '?')} — {kwh} — {p.get('location', '?')} — {p.get('progress', 0)}%")
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


@mcp.tool(
    name="oem_portal_list_sheets",
    annotations={
        "title": "List Technical Sheets",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def oem_portal_list_sheets(params: DashboardInput) -> str:
    """List all technical compliance sheets across projects.

    Args:
        params: response_format — 'markdown' or 'json'

    Returns:
        Sheet list with number, project, model, stage, score, revision.
    """
    try:
        data = await _api("sheets/")
        items = data.get("items", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        lines = [f"# Technical Sheets — {len(items)} Total\n"]
        lines.append(_fmt_table(
            items,
            ["sheet_number", "project_name", "component_model_name", "workflow_stage", "compliance_score", "revision"],
            ["Sheet", "Project", "Model", "Stage", "Score", "Rev"],
        ))
        return "\n".join(lines)

    except Exception as e:
        return _err(e)


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
