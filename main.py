from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import uvicorn

app = FastAPI(title="Twenty Workflow Receiver")


@app.post("/twenty-webhook")
async def receive_twenty_webhook(
    request: Request,
    content_type: Optional[str] = Header(None, alias="content-type"),
):
    """
    Endpoint to capture data from Twenty HTTP Request action.
    Expects application/x-www-form-urlencoded or JSON.
    """
    # Try to parse based on content-type sent from Twenty
    body_data: Dict[str, Any] = {}

    if content_type and "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        body_data = dict(form)
    else:
        # fallback to JSON
        try:
            body_data = await request.json()
        except Exception:
            # last resort: raw text
            raw = await request.body()
            body_data = {"raw_body": raw.decode("utf-8")}

    # Extract expected fields from your workflow config
    # Workflow body has keys: id, opportunity_name, new_stage_value
    opportunity_id = body_data.get("id")
    opportunity_name = body_data.get("opportunity_name")
    new_stage_value = body_data.get("new_stage_value")

    # Here you can do whatever you want:
    # - log to DB
    # - push to another service
    # - trigger internal logic
    print("Received from Twenty:", body_data)

    return JSONResponse(
        {
            "status": "ok",
            "received": {
                "id": opportunity_id,
                "opportunity_name": opportunity_name,
                "new_stage_value": new_stage_value,
            },
            "raw": body_data,
        }
    )


if __name__ == "__main__":
    # Run on port 1000
    uvicorn.run("main:app", host="0.0.0.0", port=1000, reload=True)
