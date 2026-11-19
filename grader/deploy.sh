#!/usr/bin/env bash
# Build the grader image with Cloud Build and deploy it to Cloud Run.
#   ./grader/deploy.sh setup        one-time: APIs, image repo, no-permission service account,
#                                   a VPC with no internet route for the service's egress
#   ./grader/deploy.sh              build and deploy
#   ./grader/deploy.sh killswitch   one-time, after the first deploy: $1 budget (BUDGET=n to
#                                   change) that makes the grader internal-only when reached
#   SELFTEST="1 14 16" ./grader/deploy.sh   also run check.py --selftest on those sections in
#                                   the image first (SELFTEST=all for every section)
# Uses the gcloud project from `gcloud config set project ...`.
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT=$(gcloud config get-value project 2>/dev/null)
REGION=${REGION:-us-central1}
SERVICE=vhdlbits-grader
SA=grader-runtime@$PROJECT.iam.gserviceaccount.com
REPO=$REGION-docker.pkg.dev/$PROJECT/vhdlbits
[ -n "$PROJECT" ] || { echo "no project: gcloud config set project <id>"; exit 1; }

if [ "${1:-}" = setup ]; then
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
    artifactregistry.googleapis.com compute.googleapis.com
  gcloud artifacts repositories describe vhdlbits --location "$REGION" >/dev/null 2>&1 ||
    gcloud artifacts repositories create vhdlbits --location "$REGION" --repository-format docker
  # Keep the last 3 images so storage stays inside the free 0.5 GB.
  cat > /tmp/vhdlbits-cleanup.json <<'EOF'
[{"name": "keep-3", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 3}},
 {"name": "delete-rest", "action": {"type": "Delete"}, "condition": {"tagState": "any"}}]
EOF
  gcloud artifacts repositories set-cleanup-policies vhdlbits --location "$REGION" \
    --policy /tmp/vhdlbits-cleanup.json --no-dry-run
  # The service's identity has no roles: a token stolen from the metadata server is useless.
  gcloud iam service-accounts describe "$SA" >/dev/null 2>&1 ||
    gcloud iam service-accounts create grader-runtime --display-name "VHDLBits grader (no permissions)"
  # All egress goes into this VPC, which has no NAT or internet gateway, and a firewall
  # rule drops whatever is left.
  gcloud compute networks describe grader-net >/dev/null 2>&1 ||
    gcloud compute networks create grader-net --subnet-mode custom
  gcloud compute networks subnets describe grader-subnet --region "$REGION" >/dev/null 2>&1 ||
    gcloud compute networks subnets create grader-subnet --network grader-net \
      --region "$REGION" --range 10.8.0.0/26
  gcloud compute firewall-rules describe grader-deny-egress >/dev/null 2>&1 ||
    gcloud compute firewall-rules create grader-deny-egress --network grader-net \
      --direction EGRESS --action DENY --rules all --destination-ranges 0.0.0.0/0
  echo "setup done; now run ./grader/deploy.sh"
  exit 0
fi

if [ "${1:-}" = killswitch ]; then
  # A $1 budget on this project whose notifications trigger grader/killswitch, which makes
  # the grader internal-only once spend reaches it. The trial's promotional credit is not
  # counted, so the budget sees what would really be billed; free-tier usage costs nothing.
  BUDGET=${BUDGET:-1}
  KS=killswitch@$PROJECT.iam.gserviceaccount.com
  BILLING=$(gcloud billing projects describe "$PROJECT" --format 'value(billingAccountName)' | sed 's|billingAccounts/||')
  gcloud services enable billingbudgets.googleapis.com pubsub.googleapis.com \
    cloudfunctions.googleapis.com eventarc.googleapis.com
  gcloud pubsub topics describe budget >/dev/null 2>&1 || gcloud pubsub topics create budget
  gcloud iam service-accounts describe "$KS" >/dev/null 2>&1 ||
    gcloud iam service-accounts create killswitch --display-name "VHDLBits budget kill switch"
  # Just enough to change the grader's settings (updating it needs to act as its account).
  gcloud run services add-iam-policy-binding "$SERVICE" --region "$REGION" \
    --member "serviceAccount:$KS" --role roles/run.developer >/dev/null
  gcloud iam service-accounts add-iam-policy-binding "$SA" \
    --member "serviceAccount:$KS" --role roles/iam.serviceAccountUser >/dev/null
  gcloud functions deploy vhdlbits-killswitch --gen2 --region "$REGION" --runtime python312 \
    --source grader/killswitch --entry-point on_budget --trigger-topic budget \
    --service-account "$KS" --max-instances 1 --memory 256Mi \
    --set-env-vars "GRADER_SERVICE=projects/$PROJECT/locations/$REGION/services/$SERVICE"
  # The budget's Pub/Sub trigger calls the function as the same account.
  gcloud run services add-iam-policy-binding vhdlbits-killswitch --region "$REGION" \
    --member "serviceAccount:$KS" --role roles/run.invoker >/dev/null
  if ! gcloud billing budgets list --billing-account "$BILLING" \
       --format 'value(displayName)' | grep -qx vhdlbits; then
    gcloud billing budgets create --billing-account "$BILLING" --display-name vhdlbits \
      --budget-amount "${BUDGET}USD" --filter-projects "projects/$PROJECT" \
      --credit-types-treatment include-specified-credits \
      --filter-credit-types FREE_TIER,DISCOUNT,SUSTAINED_USAGE_DISCOUNT \
      --threshold-rule percent=0.5 --threshold-rule percent=0.9 --threshold-rule percent=1.0 \
      --notifications-rule-pubsub-topic "projects/$PROJECT/topics/budget"
  fi
  echo "kill switch armed at \$$BUDGET"
  exit 0
fi

SECTIONS=${SELFTEST:-}
[ "$SECTIONS" = all ] && SECTIONS=$(seq -s ' ' 1 16)
IMAGE=$REPO/grader:$(date +%Y%m%d-%H%M%S)
gcloud builds submit --config grader/cloudbuild.yaml \
  --substitutions "_IMAGE=$IMAGE,_SELFTEST=$SECTIONS" .

# The key the Cloudflare Worker sends; created on the first deploy and kept after that.
KEY_FLAG=()
if ! gcloud run services describe "$SERVICE" --region "$REGION" >/dev/null 2>&1; then
  KEY_FLAG=(--set-env-vars "GRADER_KEY=$(openssl rand -hex 32)")
fi

# One instance handling one request at a time, billed only while handling it: the most
# it can burn is one vCPU, and the budget kill switch catches anything beyond that.
gcloud run deploy "$SERVICE" --image "$IMAGE" --region "$REGION" \
  --service-account "$SA" --allow-unauthenticated \
  --execution-environment gen2 --cpu 1 --memory 1Gi --cpu-throttling \
  --min-instances 0 --max-instances 1 --concurrency 1 --timeout 30 \
  --network grader-net --subnet grader-subnet --vpc-egress all-traffic \
  ${KEY_FLAG[@]+"${KEY_FLAG[@]}"}
