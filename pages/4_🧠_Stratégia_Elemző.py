import streamlit as st
import utils
import os
st.set_page_config(page_title="Stratégia Elemző", page_icon="🧠", layout="wide")
utils.set_design()
st.title("🧠 MBO Stratégia Elemző")
st.info("Kattints a nyíl ikonra a képek sarkában a nagyításhoz!")
# Feltételezzük, hogy létrehozol egy 'images' mappát a repóban és feltöltöd a képeket.
# Ha nincs kép, csak helykitöltőt mutat.
cols = st.columns(3)
image_files = ["01. Data Loading.png", "02. Analysis.png", "03. Results.png", "04. Comparison.png", "05. Inspection.png", "06. Performance.png"] # Példa nevek
for i, img_name in enumerate(image_files):
    path = f"images/{img_name}"
    with cols[i % 3]:
        if os.path.exists(path):
            st.image(path, caption=f"Stratégia {i+1}", use_container_width=True)
        else:
            # Ha nincs kép feltöltve, placeholdert használ
            st.warning(f"Képhiba: Tölts fel egy '{img_name}' képet az 'images' mappába!")
            st.image("https://via.placeholder.com/300x200?text=Kep+Hianyzi", use_container_width=True)
