import os
st.write("Archivos en el directorio actual:", os.listdir(os.getcwd()))
st.write("Base de datos existe:", os.path.exists("./db/FonotecaRadioUMH.db"))