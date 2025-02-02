consulta = "SELECT * FROM fonoteca_cd WHERE titulo_cd LIKE '%RESERVADA%';"
resultado = ejecutar_consulta(consulta)

if isinstance(resultado, pd.DataFrame) and not resultado.empty:
    st.write("### Resultados de la consulta:")
    st.dataframe(resultado)
else:
    st.warning("⚠️ No se encontraron resultados para 'RESERVADA'.")