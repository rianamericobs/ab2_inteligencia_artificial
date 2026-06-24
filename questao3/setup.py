#!/usr/bin/env python3
"""
Script de configuração e inicialização do FlightBot
Execute: python setup.py
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
import chaveAPI

def print_banner():
    print("""
╔═══════════════════════════════════════════════════╗
║         ✈️  FlightBot - Assistente de Voo          ║
║          Sistema Multi-Agente com IA              ║
╚═══════════════════════════════════════════════════╝
""")

def check_python():
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ é necessário. Sua versão:", sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")

def install_deps():
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"
        ])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        sys.exit(1)

def check_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  GEMINI_API_KEY não encontrada!")
        print("   Configure com: export GEMINI_API_KEY='sua-chave-aqui'")
        print("   Obtenha sua chave GRATUITA em: https://aistudio.google.com/apikey\n")
        
        key = input("   Ou insira sua chave agora (Enter para pular): ").strip()
        if key:
            os.environ["GEMINI_API_KEY"] = key
            print("✅ Chave configurada para esta sessão")
        else:
            print("⚠️  Continuando sem a chave (o servidor pode falhar)")
    else:
        masked = api_key[:8] + "..." + api_key[-4:]
        print(f"✅ GEMINI_API_KEY encontrada: {masked}")

def open_browser_delayed():
    time.sleep(2.5)
    webbrowser.open("frontend/index.html")
    print("\n🌐 Frontend aberto no navegador!")
    print("   Se não abriu automaticamente, abra: frontend/index.html")

def start_server():
    print("\n🚀 Iniciando servidor FlightBot em http://localhost:8000")
    print("   Docs da API: http://localhost:8000/docs")
    print("   Pressione Ctrl+C para parar\n")
    
    # Abre o frontend no navegador após 2.5s
    t = threading.Thread(target=open_browser_delayed, daemon=True)
    t.start()
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 FlightBot encerrado. Até logo!")

def run_cli_only():
    print("\n🤖 Iniciando FlightBot no terminal (modo CLI)...")
    subprocess.run([sys.executable, "backend/agents.py"])

if __name__ == "__main__":
    print_banner()
    check_python()
    
    print("\nEscolha o modo de execução:")
    print("  1) Interface Web (recomendado) + API")
    print("  2) Terminal (CLI)")
    print("  3) Instalar dependências apenas")
    
    choice = input("\nOpção [1]: ").strip() or "1"
    
    if choice == "3":
        install_deps()
        print("\n✅ Dependências instaladas! Execute novamente para iniciar.")
    elif choice == "2":
        check_api_key()
        install_deps()
        run_cli_only()
    else:
        check_api_key()
        install_deps()
        start_server()
