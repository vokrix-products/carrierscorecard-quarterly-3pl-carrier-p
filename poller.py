import os, time, json, requests, traceback

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
REST_URL = f"{SUPABASE_URL}/rest/v1"

SB_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

import processor

def download_file(bucket, file_path):
    if file_path.startswith(bucket + "/"):
        file_path = file_path[len(bucket) + 1:]
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY})
    resp.raise_for_status()
    return resp.content

def process_job(job):
    job_id = job["id"]
    customer_id = job.get("customer_id")
    input_file_path = job["input_file_path"]

    try:
        file_bytes = download_file("uploads", input_file_path)
        records = processor.process_file(file_bytes)

        for r in records:
            payload = {
                "product_id": PRODUCT_ID,
                "customer_id": customer_id,
                "title": r["title"],
                "status": r["status"],
                "details": r["details"],
                "source_file_path": input_file_path,
                "due_date": r.get("due_date")
            }
            requests.post(
                f"{REST_URL}/records",
                headers={**SB_HEADERS, "Prefer": "return=minimal"},
                json=payload
            )

        result = {
            "job_id": job_id,
            "records_created": len(records),
            "status": "completed"
        }
        result_filename = f"{job_id}.json"
        result_bytes = json.dumps(result)

        upload_headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
            "Content-Type": "application/json"
        }
        upload_resp = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/results/{result_filename}",
            headers=upload_headers,
            data=result_bytes
        )
        upload_resp.raise_for_status()

        output_file_path = f"results/{result_filename}"
        requests.patch(
            f"{REST_URL}/jobs?id=eq.{job_id}",
            headers={**SB_HEADERS, "Prefer": "return=minimal"},
            json={
                "status": "completed",
                "output_file_path": output_file_path,
                "result_summary": f"Processed {len(records)} records",
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        )

        try:
            notif_payload = {
                "product_id": PRODUCT_ID,
                "customer_id": customer_id,
                "title": "Processing complete",
                "body": "Your upload has been processed successfully.",
                "type": "success",
                "read": False
            }
            requests.post(
                f"{REST_URL}/notifications",
                headers={**SB_HEADERS, "Prefer": "return=minimal"},
                json=notif_payload
            )
        except Exception:
            pass

    except Exception as e:
        requests.patch(
            f"{REST_URL}/jobs?id=eq.{job_id}",
            headers={**SB_HEADERS, "Prefer": "return=minimal"},
            json={
                "status": "failed",
                "result_summary": str(e),
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        )

        try:
            notif_payload = {
                "product_id": PRODUCT_ID,
                "customer_id": customer_id,
                "title": "Processing failed",
                "body": "There was an error processing your upload.",
                "type": "error",
                "read": False
            }
            requests.post(
                f"{REST_URL}/notifications",
                headers={**SB_HEADERS, "Prefer": "return=minimal"},
                json=notif_payload
            )
        except Exception:
            pass

def poll():
    while True:
        try:
            resp = requests.get(
                f"{REST_URL}/jobs",
                headers=SB_HEADERS,
                params={
                    "status": "eq.pending",
                    "job_type": "eq.process_upload",
                    "product_id": f"eq.{PRODUCT_ID}",
                    "select": "*"
                }
            )
            jobs = resp.json()
            for job in jobs:
                process_job(job)
        except Exception as e:
            print("Poller error:", e)
        time.sleep(60)

if __name__ == "__main__":
    print("Poller started")
    poll()
