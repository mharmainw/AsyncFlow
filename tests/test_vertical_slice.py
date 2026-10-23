import csv
import io
import os
import time

import httpx


API_URL = os.getenv("ASYNCFLOW_API_URL", "http://localhost")


def wait_for_api(client: httpx.Client):
    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        try:
            if client.get("/openapi.json").status_code == 200:
                return
        except httpx.TransportError:
            pass

        time.sleep(0.25)

    raise AssertionError("AsyncFlow API did not become ready within 30 seconds")


def test_uploaded_csv_is_processed_and_downloadable():
    with httpx.Client(base_url=API_URL, timeout=10.0) as client:
        wait_for_api(client)

        upload_response = client.post(
            "/jobs",
            params=[
                ("operation", "clean"),
                ("missing_value_policy", "preserve"),
                ("required_columns", "name"),
                ("required_columns", "age"),
            ],
            files={
                "file": (
                    "people.csv",
                    "name,age\n Alice ,30\nAlice,30\nBob,40\n",
                    "text/csv",
                )
            },
        )

        assert upload_response.status_code == 202
        job_id = upload_response.json()["id"]

        deadline = time.monotonic() + 30
        while True:
            status_response = client.get(f"/jobs/{job_id}")
            assert status_response.status_code == 200
            status = status_response.json()["status"]

            if status in {"completed", "failed"}:
                break
            if time.monotonic() >= deadline:
                raise AssertionError(f"Job {job_id} did not finish within 30 seconds")

            time.sleep(0.25)

        assert status == "completed", status_response.json()

        result_response = client.get(f"/jobs/{job_id}/result")

        assert result_response.status_code == 200
        assert result_response.headers["content-type"].startswith("text/csv")
        assert "attachment" in result_response.headers["content-disposition"]
        assert list(csv.DictReader(io.StringIO(result_response.text))) == [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "40"},
        ]
