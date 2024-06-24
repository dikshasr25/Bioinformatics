import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle
import gdown
import requests
import sklearn
# Function to download the model from Google Drive
def download_model(url, output):
    gdown.download(url, output, quiet=False)

# Download and load the model
model_url = 'https://drive.google.com/uc?id=1ZmWYj5SITeL1MJJyJ4tOJYdYMZ4uK_8V'
output_model = 'model.pkl'

# Download the model if it does not exist
if not os.path.exists(output_model):
    download_model(model_url, output_model)

# Load the model
try:
    with open(output_model, 'rb') as file:
        model = pickle.load(file)
except Exception as e:
    st.error(f"Error loading the model: {e}")

# Function to display the logo image
def display_logo(url):
    try:
        image = Image.open(requests.get(url, stream=True).raw)
        st.image(image, use_column_width=True)
    except Exception as e:
        st.error(f"Error loading the logo image: {e}")

# Display the logo
logo_url = 'https://github.com/dikshasr25/Bioinformatics/blob/9442d62380f0d6b30fd6122587bf176c324f9ba6/Bioactivity_Prediction_App/logo.png?raw=true'
display_logo(logo_url)

# Page title
st.markdown("""
# Bioactivity Prediction App (IDO1)

This app allows you to predict the bioactivity towards inhibiting the `IDO1` enzyme. `Indoleamine 2, 3-dioxygenase 1 (IDO1)` is a drug target for Cancer Immunotherapy. It is also a potential target for autoimmune diseases.

**Credits**
- App built in `Python` + `Streamlit` by [Diksha Singh Rathore](https://github.com/@dikshasr25)
- Descriptor calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[Read the Paper]](https://doi.org/10.1002/jcc.21707).
---
""")

# Sidebar
with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
    st.sidebar.markdown("""
[Example input file](https://github.com/dikshasr25/Bioinformatics/blob/d9b92feae5963773f33236ea0c233481f23169d5/Bioactivity_Prediction_App/IDO1.txt)
""")

# Molecular descriptor calculator
def desc_calc():
    # Perform the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building
def build_model(input_data):
    try:
        # Apply model to make predictions
        prediction = model.predict(input_data)
        st.header('**Prediction output**')
        prediction_output = pd.Series(prediction, name='pIC50')
        molecule_name = pd.Series(load_data[1], name='molecule_name')
        df = pd.concat([molecule_name, prediction_output], axis=1)
        st.write(df)
        st.markdown(filedownload(df), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error in model prediction: {e}")

if st.sidebar.button('Predict'):
    if uploaded_file is not None:
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

        st.header('**Original input data**')
        st.write(load_data)

        with st.spinner("Calculating descriptors..."):
            desc_calc()

        # Read in calculated descriptors and display the dataframe
        st.header('**Calculated molecular descriptors**')
        desc = pd.read_csv('descriptors_output.csv')
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
        st.error('Please upload a file to start the prediction.')
else:
    st.info('Upload input data in the sidebar to start!')
