import streamlit as st
import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://qualysapi.qg2.apps.qualys.com/api/2.0/fo"
delete_url = f"{BASE_URL}/report/"
headers = {"X-Requested-With": "Python Script"}

def fetch_delete_reprot_id(session_id):
	payload = {"action": "list"}
	cookies = {"QualysSession": session_id}

	response = requests.post(delete_url, headers=headers, cookies=cookies, data=payload)

	if response.status_code == 200:
		#st.write(response.text)
		delete_data = []
		checklist_data = []
		root = ET.fromstring(response.text)
		for scan in root.findall(".//REPORT"):
			delete_id = scan.findtext("ID")
			title = scan.findtext("TITLE")
			if delete_id:
				delete_data.append(delete_id)
				checklist_data.append({
					"id": delete_id,
					"title": title
					})

		return checklist_data

	else: return(response.status_code)

def delete_report(delete_data_id, delete_data_title, session_id):
	cookies = {"QualysSession": session_id}
	for i in range (0,len(delete_data_id)):
		payload = {"action": "delete", "id": delete_data_id[i]}

		response = requests.post(delete_url, headers=headers, cookies=cookies, data=payload)

	if response.status_code == 200:
	    st.success(f"Successfully deleted reports: {delete_data_title}")
	    return True
	else:
	    st.error(f"Failed to delete. Error: {response.text}")
	    return False


