### **Qualys-Flow**

---
This is a Qualys automation build on Streamlit web framework. It solves the latency time that comes with Qualys UI.

---
**_Requirements_**

---
- Python3
- Python `pip3`
- Streamlit
- Steamlit_Option_Menu

---
**_Installation_**

---
- cd to Qualys-Flow directory
- install requirements : `pip install -r requirements.txt`
- run: `streamlit run app.py`
- you will be able to access it on your `http://localhost:8501`

**_OR_**
Build docker image

---
- cd to Qualys-Flow directory
- build docker image: `sudo docker build -t qualys-flow .`
- initiate container: `sudo docker run -p 8501:8501 -v $(pwd)/downloads:/app/downloads qualys-flow`


**_Feature_**

---
- Generate and Download scan reports
- Download already generated reports
- Delete reports to save spaces, as Qualys provide limited user space

*_Configuration_**

---
- Obtain the template ID from the qualys
- Make necessary in the `Qualys-Flow/qualys/reports.py` and `Qualys-Flow/qualys/config.py`

**_TODO_**

---
- Add support for launching scans for VM
- Add web application support and all its functionality

