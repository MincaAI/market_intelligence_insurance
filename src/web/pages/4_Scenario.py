# Other Analysis
import streamlit as st
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path pour importer nos modules
root_path = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_path))

from agent.graph import compile_agent
from agent.state import CompareState

def run_agent_comparison(initial_state: CompareState):
    """
    Exécute l'agent de comparaison et retourne les résultats.
    """
    try:
        # Compiler l'agent
        agent = compile_agent()
        
        # Exécuter l'agent
        final_state = agent.invoke(initial_state)
        
        return final_state
        
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de l'agent : {str(e)}")
        return None

def display_chunk_results(title: str, result_text: str, color: str):
    """
    Affiche les résultats des chunks de manière formatée et robuste.
    """
    st.markdown(f"### {title}")
    
    if "Aucun résultat trouvé" in result_text:
        st.warning(result_text)
        return
    
    # Les chunks sont séparés par une double nouvelle ligne ('\n\n') dans le node RAG.
    # On peut donc splitter le texte sur ce délimiteur.
    # On ignore le premier élément qui est l'en-tête (ex: "Résultats AXA...")
    chunks = result_text.strip().split('\n\n')[1:]
    
    if not chunks:
        # Au cas où le format serait inattendu, on affiche le texte brut.
        st.info(result_text)
        return

    for chunk_str in chunks:
        if not chunk_str.strip():
            continue
            
        # On remplace les sauts de ligne par des <br> pour l'affichage en HTML
        html_chunk = chunk_str.replace('\n', '<br>')
        
        st.markdown(
            f"<div style='background-color: {color}20; padding: 10px; border-radius: 5px; margin: 5px 0;'>{html_chunk}</div>",
            unsafe_allow_html=True
        )

def main():
    st.set_page_config(
        page_title="Comparaison Assurance Auto",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("⚖️ Comparaison AXA vs Generali")

    # Section 1: Sélection du produit
    st.header("1. Choisissez le type d'assurance")
    insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))
    product_type = insurance_type.lower()
    
    # Section 2: Input utilisateur et bouton
    st.header(f"2. Que voulez-vous comparer pour l'assurance {insurance_type.lower()} ?")
    user_query = st.text_area(
        "Indiquez ici le sujet de comparaison :",
        placeholder=f"Ex: Quelles sont les franchises pour l'assurance {insurance_type.lower()} ?",
        height=100,
        label_visibility="collapsed"
    )
    
    run_button = st.button(
        "🚀 Lancer la Comparaison",
        type="secondary"
    )
    
    # Section 3: Exécution et affichage des résultats
    if run_button and user_query.strip():
        st.markdown("---")
        
        with st.spinner("🔄 Exécution de l'agent de comparaison..."):
            # On passe le type de produit à l'état initial
            initial_state = CompareState(
                user_input=user_query,
                product=product_type,
                detected_category="",
                axa_result="",
                generali_result="",
                comparison=""
            )
            results = run_agent_comparison(initial_state)
        
        if results:
            # Affichage de la catégorie détectée
            st.success(f"🏷️ **Catégorie détectée :** {results['detected_category']}")
            
            # Section 4: Deux colonnes pour les réponses des agents
            st.header("📊 Résultats des Agents")
            
            col1, col2 = st.columns(2)
            
            with col1:
                display_chunk_results("🔵 Agent AXA", results['axa_result'], "#0066cc")
            
            with col2:
                display_chunk_results("🟢 Agent Generali", results['generali_result'], "#00cc66")
            
            # Section 5: Tableau comparatif
            st.markdown("---")
            st.subheader("📋 Tableau Comparatif")
            
            # Afficher la comparaison finale
            if results['comparison']:
                st.markdown(results['comparison'])
            else:
                st.warning("Aucune comparaison générée.")
            
            # Section 6: Informations supplémentaires
            st.markdown("---")
            st.header("ℹ️ Informations Techniques")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**Requête :** {user_query}")
            
            with col2:
                st.info(f"**Catégorie :** {results['detected_category']}")
            
            with col3:
                st.info("**Statut :** ✅ Terminé")
    
    elif run_button and not user_query.strip():
        st.error("❌ Veuillez saisir une question avant de lancer la comparaison.")

if __name__ == "__main__":
    main() 