import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

st.sidebar.title('🎈 SNMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model. For more information, read the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')

def render(pdb):
    pdbview = py3Dmol.view()
    pdbview.addModel(pdb, 'pdb')
    pdbview.setStyle({'cartoon': {'color': 'spectrum'}})
    pdbview.setBackgroundColor('white')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    pdbview.spin(True)
    showmol(pdbview, height=500, width=800)

DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)

def update(sequence=txt):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence, verify=False)
    
    if response.status_code == 200:
        pdb_string = response.content.decode('utf-8')
        
        if "ATOM" not in pdb_string:
            st.error("The response does not contain valid PDB data.")
            return
        
        with open('predicted.pdb', 'w') as f:
            f.write(pdb_string)

        try:
            struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
            b_value = round(struct.b_factor.mean(), 4)

            st.subheader('Visualization of predicted protein structure')
            render(pdb_string)

            st.subheader('plDDT')
            st.write('plDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
            st.info(f'plDDT: {b_value}')

            st.download_button(
                label="Download PDB",
                data=pdb_string,
                file_name='predicted.pdb',
                mime='text/plain',
            )
        except ValueError as e:
            st.error(f"Error loading PDB structure: {e}")
            st.text_area("PDB File Content", pdb_string)
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        st.text_area("API Response", response.text)

predict = st.sidebar.button('Predict', on_click=update)

if not predict:
    st.warning('👈 Enter protein sequence data!')
