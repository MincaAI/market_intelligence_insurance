#!/usr/bin/env python3
"""
Script de test pour l'agent LangGraph de comparaison d'assurances.
"""

from agent.graph import compile_agent
from agent.state import CompareState

def run_agent_test():
    """
    Teste l'agent avec une requête utilisateur.
    """
    print("🤖 Agent de comparaison d'assurances AXA vs Generali")
    print("=" * 60)
    
    # Demander la requête à l'utilisateur
    user_query = input("\n💬 Entrez votre question sur les assurances : ")
    
    if not user_query.strip():
        print("❌ Requête vide. Arrêt du programme.")
        return
    
    print(f"\n🔍 Traitement de votre requête : '{user_query}'")
    print("=" * 60)
    
    # Initialiser l'état
    initial_state = CompareState(
        user_input=user_query,
        detected_category="",
        axa_result="",
        generali_result="",
        comparison=""
    )
    
    try:
        # Compiler et exécuter l'agent
        print("\n📋 Compilation de l'agent...")
        agent = compile_agent()
        
        print("🚀 Exécution de l'agent...")
        print("-" * 40)
        
        # Exécuter l'agent
        final_state = agent.invoke(initial_state)
        
        # Afficher les résultats de manière structurée
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS DE L'AGENT")
        print("=" * 60)
        
        # 1. Catégorie détectée
        print(f"\n🏷️  CATÉGORIE DÉTECTÉE:")
        print(f"   {final_state['detected_category']}")
        
        # 2. Résultats AXA
        print(f"\n🔵 RÉSULTATS AXA:")
        print("-" * 30)
        print(final_state['axa_result'])
        
        # 3. Résultats Generali
        print(f"\n🟢 RÉSULTATS GENERALI:")
        print("-" * 30)
        print(final_state['generali_result'])
        
        # 4. Comparaison finale
        print(f"\n⚖️  COMPARAISON FINALE:")
        print("-" * 30)
        print(final_state['comparison'])
        
        print("\n" + "=" * 60)
        print("✅ Traitement terminé avec succès !")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution de l'agent : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_agent_test() 