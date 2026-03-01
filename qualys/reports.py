import requests
import xml.etree.ElementTree as ET
from requests.exceptions import ChunkedEncodingError, ConnectionError
import time
import streamlit as st
import os
from qualys.utils import get_target_directory, sanitize_filename

BASE_URL = "https://qualysapi.qg2.apps.qualys.com/api/2.0/fo"

CSV_TEMPLATE_ID = "2431093"
PDF_TEMPLATE_ID = "2369507"
headers = {"X-Requested-With": "Streamlit Scan Script"}

def get_scan_list(session_id):
    url = f"{BASE_URL}/scan/"
    headers = {"X-Requested-With": "Streamlit Scan Script"}
    cookies = {"QualysSession": session_id}
    params = {"action": "list"}

    response = requests.post(url, headers=headers, cookies=cookies, data=params)                                              

    if response.status_code == 200:
        return response.text
    else:
        st.error("Failed to fetch scan list")
        return None

def parse_scans(xml_data):
    scans_data = []
    root = ET.fromstring(xml_data)

    for scan in root.findall(".//SCAN"):
        ref = scan.findtext("REF")
        title = scan.findtext("TITLE") or "Untitled_Scan"

        client_name = "Unknown_Client"
        client_elem = scan.find("CLIENT")

        if client_elem is not None:
            name_elem = client_elem.find("NAME")
            if name_elem is not None and name_elem.text:
                client_name = name_elem.text.strip()

        scans_data.append({
            "REF": ref,
            "TITLE": title,
            "CLIENT": client_name
        })

    return scans_data


def launch_report(ref, title, template_id, output_format, session_id, log_placeholder):
    """Launches a report and returns the Report ID."""
    url = f"{BASE_URL}/report/"
    cookies = {"QualysSession": session_id}
    payload = {
        "action": "launch",
        "template_id": template_id,
        "report_title": title,
        "output_format": output_format,
        "report_refs": ref
    }
    response = requests.post(url, headers=headers, cookies=cookies, data=payload)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for item in root.findall(".//ITEM"):
            if item.findtext("KEY") == "ID":
                report_id = item.findtext("VALUE")
                st.info(f"    [*] {output_format.upper()} Launched. ID: {report_id}")
                return report_id
    return None

def fetch_report(report_id, title, output_format, target_dir, session_id):
    """Downloads the report file to the specified directory."""
    url = f"{BASE_URL}/report/"
    params = {"action": "fetch", "id": report_id}
    cookies = {"QualysSession": session_id}
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    if response.status_code == 200:
        safe_title = title.replace("/", "-").replace("\\", "-").replace("|", "-")
        filename = f"{safe_title}.{output_format}"
        file_path = os.path.join(target_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(response.content)
        st.info(f"    [+] Downloaded: {filename}")
    else:
        root = ET.fromstring(response.text)
        text_value = root.find(".//CODE").text
        if text_value == 2000:
            st.warning("User limit reached, reports will not be saved")
        else:
            st.warning(f"    [!] Failed download for ID {report_id}")

def wait_for_reports_to_finish(csv_id, pdf_id, session_id):
    """Wait loop to ensure reports are ready for download."""
    st.info(f"    [*] Waiting for reports to finish...")
    for _ in range(60):  # 30 minute max timeout (60 * 30s)
        finished_list = get_finished_report_ids(session_id)
        if csv_id in finished_list and pdf_id in finished_list:
            return True
        time.sleep(30)
    return False

def get_finished_report_ids(session_id):
    """Polls Qualys for reports with state=Finished."""
    url = f"{BASE_URL}/report/"
    cookies = {"QualysSession": session_id}
    params = {"action": "list", "state": "Finished"}
    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            return [report.findtext("ID") for report in root.findall(".//REPORT")]
    except:
        pass
    return []

