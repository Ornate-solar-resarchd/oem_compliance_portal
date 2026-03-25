"""
Upload files to Google Drive via the Apps Script Web App.
The Apps Script's doPost() accepts base64-encoded files and saves them to the upload folder.
"""
import os
import base64
import json
import httpx


async def upload_to_gdrive(file_bytes: bytes, file_name: str, mime_type: str = "") -> dict:
    """
    Upload a file to company Google Drive.
    Returns: {"success": True, "file": {"name", "url", "id", "size"}} or {"success": False, "error": "..."}
    """
    fetcher_url = os.environ.get("GDRIVE_FETCHER_URL", "")
    if not fetcher_url:
        print("[GDrive Upload] GDRIVE_FETCHER_URL not set — skipping upload")
        return {"success": False, "error": "GDRIVE_FETCHER_URL not configured"}

    # Guess MIME type if not provided
    if not mime_type:
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        mime_map = {
            "pdf": "application/pdf",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xls": "application/vnd.ms-excel",
            "csv": "text/csv",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    # Encode file as base64
    file_b64 = base64.b64encode(file_bytes).decode("utf-8")

    payload = {
        "fileName": file_name,
        "fileData": file_b64,
        "mimeType": mime_type,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.post(fetcher_url, json=payload)

        if resp.status_code == 200:
            result = resp.json()
            if result.get("success"):
                print(f"[GDrive Upload] Saved '{file_name}' to Drive: {result['file']['url']}")
                return result
            else:
                print(f"[GDrive Upload] Drive returned error: {result.get('error')}")
                return result
        else:
            print(f"[GDrive Upload] HTTP {resp.status_code}: {resp.text[:200]}")
            return {"success": False, "error": f"HTTP {resp.status_code}"}

    except Exception as e:
        print(f"[GDrive Upload] Error: {e}")
        return {"success": False, "error": str(e)}
