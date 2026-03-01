import streamlit as st
import requests
import xml.etree.ElementTree as ET

BaseURL = "https://qualysapi.qg2.apps.qualys.com/api/2.0/fo"


def login(username: str, password: str):
	loginURL = f"{BaseURL}/session/"
	headers = {"X-Requested-With": "StreamLit Automation"}
	payloads = {
	"action": "login",
	"username": username,
	"password": password
}

	try:
		response = requests.post(loginURL, headers=headers, data=payloads)
		root = ET.fromstring(response.text)
		text_value = root.find(".//TEXT").text

		if response.status_code == 200:
			session_cookie = response.cookies.get("QualysSession")
			if session_cookie:
				return session_cookie
		else:
			return text_value

	except Exception as e:
        	st.error(f"Login Error: {e}")
        	return None
