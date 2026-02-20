"""
Test script to verify AI matching with DeepSeek API
Run this to see if your API key works and how the AI matching behaves.
"""

import sys
import os
sys.path.append('.')

# Set up Flask app context
from app import app
from models import db
from models.user import User
from models.project import Project, Task
from utils.matching import ai_match_task_to_employees, auto_match_tasks

import requests
import json

# ===========================
# Configuration Webhook n8n
# ===========================
WEBHOOK_URL = "http://localhost:5678/webhook-test/github-automation"  # À remplacer par ton URL Ngrok


def envoyer_resultats_matching(nom_projet, employes, description="", prive=True):
    """
    Envoie les résultats du matching vers le webhook n8n pour créer le dépôt GitHub.
    """
    payload = {
        "nom_projet": nom_projet,
        "employes": employes,
        "description": description,
        "private": prive
    }
    
    headers = {"Content-Type": "application/json"}
    
        
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        print("✅ Succès ! Réponse du webhook :", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("❌ Erreur lors de l'envoi au webhook :", e)
        if hasattr(e, 'response') and e.response is not None:
            print("Détails :", e.response.text)
        return None

# ===========================
# Création des données de test
# ===========================
def create_test_data():
    """Create some test employees and tasks"""
    with app.app_context():
        # Clear existing test data
        User.query.filter(User.username.like('test_%')).delete()
        db.session.commit()
        
        # Create test employees
        emp1 = User(
            username='test_frontend_dev',
            name='Alice Johnson', 
            role='employee',
            status='active',
            technical_skills={
                'frontend': ['React', 'JavaScript', 'HTML', 'CSS'],
                'tools': ['Git', 'VS Code']
            },
            years_of_experience=3,
            password_hash='dummy'
        )
        
        emp2 = User(
            username='test_backend_dev',
            name='Bob Smith',
            role='employee', 
            status='active',
            technical_skills={
                'backend': ['Python', 'Flask', 'SQL', 'PostgreSQL'],
                'tools': ['Docker', 'Git']
            },
            years_of_experience=5,
            password_hash='dummy'
        )
        
        emp3 = User(
            username='test_fullstack_dev',
            name='Carol Wilson',
            role='employee', 
            status='active',
            technical_skills={
                'frontend': ['React', 'TypeScript'],
                'backend': ['Node.js', 'Express', 'MongoDB'],
                'tools': ['AWS', 'Docker']
            },
            years_of_experience=4,
            password_hash='dummy'
        )
        
        db.session.add_all([emp1, emp2, emp3])
        db.session.commit()
        
        print("✅ Test employees created:")  
        print(f"   • {emp1.full_name}: {emp1.get_all_skills()}")
        print(f"   • {emp2.full_name}: {emp2.get_all_skills()}")
        print(f"   • {emp3.full_name}: {emp3.get_all_skills()}")
        
        return [emp1, emp2, emp3]

# ===========================
# Test AI Matching
# ===========================
def test_ai_matching():
    """Test the AI matching with sample tasks"""
    with app.app_context():
        employees = create_test_data()
        
        # -----------------------------
        # Test Task 1: Simple frontend task
        # -----------------------------
        class MockTask:
            def __init__(self, nom, priorite, duree, sous_taches):
                self.nom = nom
                self.priorite = priorite
                self.duree_estimee_jours = duree
                self.sous_taches = sous_taches
        
        simple_task = MockTask(
            nom="Build user login page",
            priorite="Moyenne", 
            duree=3,
            sous_taches=[
                {'competences_requises': ['React', 'HTML', 'CSS']},
                {'competences_requises': ['JavaScript', 'Forms']}
            ]
        )
        
        matches = ai_match_task_to_employees(simple_task, employees)
        
        # ===========================
        # Envoi des résultats au webhook
        # ===========================
        employes_payload = [
            {"github_login": emp.username, "nom": emp.name.split()[-1], "prenom": emp.name.split()[0]}
            for emp in employees
        ]
        envoyer_resultats_matching(
            nom_projet=simple_task.nom,
            employes=employes_payload,
            description="Simple frontend task",
            prive=True
        )
        
        # -----------------------------
        # Test Task 2: Complex full-stack task
        # -----------------------------
        complex_task = MockTask(
            nom="Build e-commerce platform with real-time features",
            priorite="Haute",
            duree=15,
            sous_taches=[
                {'competences_requises': ['React', 'TypeScript', 'Frontend']},
                {'competences_requises': ['Python', 'Flask', 'API']}, 
                {'competences_requises': ['PostgreSQL', 'Database']},
                {'competences_requises': ['WebSockets', 'Real-time']},
                {'competences_requises': ['Docker', 'DevOps']},
                {'competences_requises': ['AWS', 'Deployment']}
            ]
        )
        
        matches = ai_match_task_to_employees(complex_task, employees)
        
        # ===========================
        # Envoi des résultats au webhook
        # ===========================
        employes_payload = [
            {"github_login": emp.username, "nom": emp.name.split()[-1], "prenom": emp.name.split()[0]}
            for emp in employees
        ]
        envoyer_resultats_matching(
            nom_projet=complex_task.nom,
            employes=employes_payload,
            description="Complex full-stack task",
            prive=True
        )

if __name__ == '__main__':
    print("🤖 Testing AI Matching with DeepSeek...")
    print("=" * 50)
    
    try:
        test_ai_matching()
        print("\n✅ AI Matching test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Possible issues:")
        print("   • Check your DeepSeek API key")
        print("   • Verify internet connection") 
        print("   • Make sure environment variable is set correctly")
