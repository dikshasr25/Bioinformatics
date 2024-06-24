import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle
import requests


def download_file(url, output_path):
    """
    Function to download file from URL and save it to output_path.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def desc_calc():
    bashCommand = "-java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_list.csv"

    try:
        # Execute the subprocess command
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check if subprocess executed successfully
        if process.returncode == 0:
            output_file = "./descriptors_list.csv"  # Assuming the file is saved in the current directory
            if os.path.exists(output_file):
                st.success("Descriptors calculation completed successfully!")
                
                # Provide download link
                st.markdown(f"### [Download descriptors_output.csv](./descriptors_list.csv)")
            else:
                st.error("Output file descriptors_output.csv not found.")
        else:
            st.error(f"Error occurred while running the command: {stderr.decode('utf-8')}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
   
# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building
def build_model(input_data):
    # Reads in saved regression model
    load_model = 'https://drive.google.com/file/d/1ZmWYj5SITeL1MJJyJ4tOJYdYMZ4uK_8V/view?usp=drive_link'
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)
def display_logo(url):
    try:
        image = Image.open(requests.get(url, stream=True).raw)
        st.image(image, use_column_width=True)
    except Exception as e:
        st.error(f"Error loading the logo image: {e}")
# Logo image
logo_url = 'https://github.com/dikshasr25/Bioinformatics/blob/9442d62380f0d6b30fd6122587bf176c324f9ba6/Bioactivity_Prediction_App/logo.png?raw=true'
display_logo(logo_url)

# Page title
st.markdown("""
# Bioactivity Prediction App (IDO1)

This app allows you to predict the bioactivity towards inhibting the IDO1 enzyme. Indoleamine 2, 3-dioxygenase 1 (IDO1) is a drug target for Cancer Immunotherapy. It is also a potential target for autoimmune diseases.

**Credits**
- App built in Python + Streamlit by [Diksha Singh Rathore](https://github.com/@dikshasr25) )
- Descriptor calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[Read the Paper]](https://doi.org/10.1002/jcc.21707).
---
""")

# Sidebar
with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
    st.sidebar.markdown("""
[Example input file](https://github.com/dikshasr25/Bioinformatics/blob/d9b92feae5963773f33236ea0c233481f23169d5/Bioactivity_Prediction_App/IDO1.txt)
""")

if st.sidebar.button('Predict'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    st.header('**Original input data**')
    st.write(load_data)

    with st.spinner("Calculating descriptors..."):
        desc_calc()

    # Read in calculated descriptors and display the dataframe
    st.header('**Calculated molecular descriptors**')
    desc = pd.read_csv('https://raw.githubusercontent.com/dikshasr25/Bioinformatics/ec86820535d24900043ad0b8beb75273f9bee8f9/Bioactivity_Prediction_App/descriptor_list.csv')
    st.write(desc)
    st.write(desc.shape)

    # Read descriptor list used in previously built model
    st.header('**Subset of descriptors from previously built models**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # Apply trained model to make prediction on query compounds
    build_model(desc_subset)
else:
    st.info('Upload input data in the sidebar to start!')  
