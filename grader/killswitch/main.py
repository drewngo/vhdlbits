"""Budget kill switch: when the project's spend reaches its budget, stop public traffic to
the grader by making its ingress internal-only. Nothing is deleted; to turn it back on:

  gcloud run services update vhdlbits-grader --region us-central1 --ingress all

Triggered by the budget's Pub/Sub notifications (grader/deploy.sh killswitch).
"""
import base64
import json
import os

import functions_framework
import google.auth
from google.auth.transport.requests import AuthorizedSession

SERVICE = os.environ["GRADER_SERVICE"]   # projects/<p>/locations/<r>/services/<s>


@functions_framework.cloud_event
def on_budget(event):
    msg = json.loads(base64.b64decode(event.data["message"]["data"]))
    cost, budget = msg.get("costAmount", 0), msg.get("budgetAmount", 0)
    print(json.dumps({"cost": cost, "budget": budget}))
    if budget <= 0 or cost < budget:
        return
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    r = AuthorizedSession(creds).patch(
        f"https://run.googleapis.com/v2/{SERVICE}?update_mask=ingress",
        json={"ingress": "INGRESS_TRAFFIC_INTERNAL_ONLY"})
    print(f"budget reached: grader ingress set to internal only ({r.status_code} {r.text[:300]})")
    r.raise_for_status()
