import requests
import json
import time
from notification import send_email_notification, send_slack_notification


# --------------------------------------------
# Function to download PDF from a given URL
# --------------------------------------------
def scrape_data(url, name):
    try:
        response = requests.get(url, stream=True, timeout=15)
        if response.status_code == 200:
            with open(name, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("✅ Download Successful:", time.ctime())
            return True
        else:
            print("❌ Failed to download:", response.status_code)
            send_slack_notification(
                "❌ Failed to Download File",
                f"Response Status: {response.status_code}\nDownload Link: {url}\nError: {response.text}"
            )
            return False

    except Exception as e:
        print("⚠️ Exception during download:", e)
        send_slack_notification(
            "⚠️ Exception in scrape_data()",
            f"An unexpected error occurred while downloading:\nURL: {url}\nError: {e}"
        )
        return False


# --------------------------------------------
# Function to call scraper for multiple documents
# --------------------------------------------
def call_scrape_funtion():
    try:
        DOCUMENT_MAP = {
            "DPA": {
                "json_file": "json_files/dpa.json",
                "link": r"https://www.benchmarkone.com/wp-content/uploads/2018/05/GDPR-Sample-Agreement.pdf"
            },
            "JCA": {
                "json_file": "json_files/jca.json",
                "link": r"https://www.surf.nl/files/2019-11/model-joint-controllership-agreement.pdf"
            },
            "C2C": {
                "json_file": "json_files/c2c.json",
                "link": r"https://www.fcmtravel.com/sites/default/files/2020-03/2-Controller-to-controller-data-privacy-addendum.pdf"
            },
            # 🔴 Wrong link to test Slack error notification
            "SCC": {
                "json_file": "json_files/scc.json",
                "link": r"https://www.thomsonreuters.com/content/dam/ewp-m/documents/thomsonreuters/en/pdf/global-sourcing-procurement/eu-eea-standard-contractual-clauses-v09-2021.pdf"
            },
            "subprocessing": {
                "json_file": "json_files/subprocessing.json",
                "link": r"https://greaterthan.eu/wp-content/uploads/Personal-Data-Sub-Processor-Agreement-2024-01-24.pdf"
            }
        }

        temp_agreement = "temp_agreement.pdf"
        summary = []
        success_count = 0
        failure_count = 0

        for key, value in DOCUMENT_MAP.items():
            print(f"🔍 Scraping document: {key}")
            success = scrape_data(value["link"], temp_agreement)

            if success:
                summary.append(f"✅ {key}: Downloaded successfully at {time.ctime()}")
                success_count += 1
            else:
                summary.append(f"❌ {key}: Download failed.")
                failure_count += 1

        # ✅ Send one email summary after all downloads
        final_summary = (
            f"📄 Compliance Scraping Summary\n\n"
            f"✅ Successful Downloads: {success_count}\n"
            f"❌ Failed Downloads: {failure_count}\n\n"
            + "\n".join(summary)
        )

        send_email_notification("Compliance Report Summary", final_summary)

    except Exception as e:
        print("❌ Error Occurred in Scraping:", e)
        send_slack_notification(
            "⚠️ Error Occurred in Scraping",
            f"Error Details: {e}"
        )
