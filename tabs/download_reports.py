import streamlit as st
import requests
import sys
import xml.etree.ElementTree as ET


BASE_URL = "https://qualysapi.qg2.apps.qualys.com/api/2.0/fo"

def fetch_generated_reports(session_id):
	cookies = {"QualysSession": session_id}
	payload = {
	"action": "list"
	}
	headers = {
	"X-Requested-With": "Streamlit Scan Script",
	"Accept": "application/xml"}

	report_url = f"{BASE_URL}/report/"

	response = requests.post(report_url, headers=headers, cookies=cookies, data=payload)
	
	if response.status_code == 200:
		report_xmldata = response.text
		
		report_data = []
		root = ET.fromstring(report_xmldata)
		for scan in root.findall(".//REPORT"):
			report_id = scan.findtext("ID")
			title = scan.findtext("TITLE")
			output_format = scan.findtext("OUTPUT_FORMAT")
			launch_datetime = scan.findtext("LAUNCH_DATETIME")
			report_data.append({
				"report_id": report_id, 
				"title": title, 
				"output_format": output_format, 
				"launch_datetime": launch_datetime
				})
		return report_data

	else: return response.status_code
