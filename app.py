import streamlit as st
from qualys.auth import login
from qualys.reports import (get_scan_list, parse_scans, launch_report, fetch_report, wait_for_reports_to_finish)
import time
from qualys.utils import get_target_directory
from qualys.config import BASE_URL, CSV_TEMPLATE_ID, PDF_TEMPLATE_ID
from tabs.download_reports import fetch_generated_reports
from tabs.delete_reports import (fetch_delete_reprot_id, delete_report)
from streamlit_option_menu import option_menu



# ---------------------------
# SESSION STATE INIT
# ---------------------------

defaults = {"authenticated": False, "session_id": None, "scans": None, "launched_reports": None}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value



# -----------------------
# LOGIN PAGE
# -----------------------
if not st.session_state.authenticated:
    st.title("Qualys Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        session = login(username, password)

        if session and len(session) == 32:
            st.session_state.session_id = session
            st.session_state.authenticated = True

            # 🔥 AUTO FETCH SCANS LAUNCHED IMMEDIATELY for def (page_2)
            launched_reports1 = fetch_generated_reports(session)
            st.session_state.launched_reports = launched_reports1

            # 🔥 AUTO FETCH SCANS IMMEDIATELY for def (page_1)
            xml_data = get_scan_list(session)
            if xml_data:
                st.write("SCAN LIST FOUND")
                st.session_state.scans = parse_scans(xml_data)

                st.rerun()
            else:
                st.error(f"Login failed : Reason: {session}")

        else:
            st.error(f"Login failed : Reason: {session}")

# DASHBOARD

else:
    def page_1():
        st.success("Logged in successfully")
        st.set_page_config(layout="wide")
        st.title("Qualys Report Portal")
        if not st.session_state.scans:
            st.warning("No scans found.")
            st.stop()

        
        scans = st.session_state.scans

        # =============================
        # CLIENT CHECKBOX SECTION
        # =============================
        st.subheader("Select Clients")

        unique_clients = sorted(set(s["CLIENT"] for s in scans))

        selected_clients = []
        cols = st.columns(3)

        for i, client in enumerate(unique_clients):
            if cols[i % 3].checkbox(client):
                selected_clients.append(client)

        # Filter scans based on client selection
        filtered_scans = scans
        if selected_clients:
            filtered_scans = [
                s for s in scans
                if s["CLIENT"] in selected_clients
            ]


        # =============================
        # SCAN CHECKBOX SECTION
        # =============================
        st.subheader("Select Scans")

        selected_scans = []

        for i, scan in enumerate(filtered_scans):
            label = f"{scan['TITLE']} ({scan['CLIENT']})"
            if st.checkbox(label, key=f"scan_{i}"):
                selected_scans.append(scan)

        # =============================
        # LAUNCH BUTTON
        # =============================
        if st.button("Launch Reports"):
            if not selected_scans:
                st.warning("Please Select at least one scan.")
                st.stop()

            log_placeholder = st.empty()
            progress = st.progress(0)
            status = st.empty()
            final_data_store = []
            total = len(selected_scans)
            for index, scan in enumerate(selected_scans, 1):
                client_name = scan['CLIENT'].split(None, 1)[0]
                ref, title = scan['REF'], scan['TITLE']

                current_target_dir = get_target_directory(client_name)
                status.info(f"Launching reports for {scan['TITLE']}")

                csv_id = launch_report(ref, title, CSV_TEMPLATE_ID, "csv", st.session_state.session_id,log_placeholder)
                pdf_id = launch_report(ref, title, PDF_TEMPLATE_ID, "pdf", st.session_state.session_id,log_placeholder)

                if csv_id and pdf_id:
                    if wait_for_reports_to_finish(csv_id, pdf_id, st.session_state.session_id):
                        fetch_report(csv_id, title, "csv", current_target_dir, st.session_state.session_id)
                        fetch_report(pdf_id, title, "pdf", current_target_dir, st.session_state.session_id)

                scan_info = {"REF": ref, "TITLE": title, "CSV_ID": csv_id, "PDF_ID": pdf_id, "CLIENT": client_name}
                final_data_store.append(scan_info)

                # 4. Throttling
                if index % 5 == 0 and index < total:
                    st.warning("[!] Pausing 120s to avoid API rate limiting...")
                    time.sleep(120)

                progress.progress(index / total)

            st.success("All selected reports processed.")

    def page_2():
        if not st.session_state.launched_reports:
            st.warning("No scans found.")
            st.error(st.session_state.launched_reports)
            st.stop()

        generated_reports = st.session_state.launched_reports
        second_generated_report = fetch_generated_reports(st.session_state.session_id)

        # Update Generated Report List if neccessary
        if len(generated_reports) < len(second_generated_report):
            generated_reports = second_generated_report

        # =============================
        # CLIENT CHECKBOX SECTION
        # =============================
        st.subheader("Select Clients")

        unique_clients = sorted(set(s["title"] for s in generated_reports))

        selected_clients = []
        cols = st.columns(3)

        for i, client in enumerate(unique_clients):
            if cols[i % 3].checkbox(client):
                selected_clients.append(client)

        # Filter scans based on client selection
        filtered_scans = generated_reports
        if selected_clients:
            filtered_scans = [
                s for s in generated_reports
                if s["title"] in selected_clients
            ]

        # =============================
        # SCAN CHECKBOX SECTION
        # =============================

        st.subheader("Select Scans")

        selected_scans = []

        for i, scan in enumerate(filtered_scans):
            label = f"{scan['title']} ({scan['launch_datetime']}) ({scan['output_format']})"
            if st.checkbox(label, key=f"scan_{i}"):
                selected_scans.append(scan)
        # =============================
        # LAUNCH BUTTON
        # =============================
        if st.button("Launch Reports"):
            if not selected_scans:
                st.warning("Please Select at least one scan.")
                st.stop()

            progress = st.progress(0)
            status = st.empty()
            final_data_store = []
            total = len(selected_scans)
            for index, scan in enumerate(selected_scans, 1):
                output_format = scan['output_format']
                report_id, title = scan['report_id'], scan['title']

                client_name = scan['title'].split(None, 1)[0]
                current_target_dir = get_target_directory(client_name)
                
                status.info(f"Launching reports for {scan['title']}")
                
                if output_format == "CSV":                    
                    fetch_report(report_id, title, "csv", current_target_dir, st.session_state.session_id)
                    st.success("All selected reports processed.")
                else:
                    fetch_report(report_id, title, "pdf", current_target_dir, st.session_state.session_id)
                    st.success("All selected reports processed.")

    def page_3():
        checklisting = fetch_delete_reprot_id(st.session_state.session_id)
        st.subheader("Select Reports To Delete")

        selected_scans_id = []
        selected_scans_title = []

        for i, scan in enumerate(checklisting):
            label = f"{scan['title']} (ID: {scan['id']})"
            if st.checkbox(label, key=f"scan_{i}"):
                selected_scans_id.append(scan['id'])
                selected_scans_title.append(scan['title'])

        #st.info(f"Selected_scan - {selected_scans_title} - {selected_scans_id}")
        if st.button("Delete Reports"):
            if selected_scans_id:
            # Pass the whole list at once
                success = delete_report(selected_scans_id, selected_scans_title, st.session_state.session_id)
                if success:
                    st.info("Refreshing...") 
                    # to refresh the list and show they are gone
                    st.rerun()
            else:
                st.warning("Please select at least one report to delete.")

    # PAGE SETUP
    launch_reports = st.Page(
        page_1,
        title="Qualys Report Portal"
        )
    download_reports = st.Page(
        page_2,
        title="Download Reports"
        )
    delete_report_page = st.Page(
        page_3,
        title="Delete Reports"
        )

    if st.session_state.authenticated:
        pg = st.navigation({"Dashboard": [launch_reports, download_reports, delete_report_page]})
    else:
        pg = st.navigation([login_page])

    pg.run()
