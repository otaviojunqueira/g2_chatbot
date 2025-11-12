from flask import Flask, request
import requests
import os

app = Flask(__name__)

# "Memória" simples para armazenar o estado de cada usuário
user_states = {}

# Fluxo de atendimento (resumido aqui, mas você pode expandir com todos os nós)
fluxo = {
    "inicio": {
        "mensagem": (
            "Olá! 👋 Seja bem-vindo(a) à g2 soluções contábeis!\n"
            "Com qual profissional estou falando?\n"
            "1️⃣ Médico(a)\n2️⃣ Dentista\n3️⃣ Fisioterapeuta\n4️⃣ Psicólogo(a)\n0️⃣ Falar com especialista"
        ),
        "opcoes": {
            "1": "medico",
            "2": "dentista",
            "3": "fisioterapeuta",
            "4": "psicologo",
            "0": "especialista"
        }
    },
    "medico": {
        "mensagem": (
            "Entendido! Como posso te ajudar hoje?\n"
            "1️⃣ Sou estudante ou recém-formado\n"
            "2️⃣ Faço plantões ou atendo como PF\n"
            "3️⃣ Já tenho CNPJ\n"
            "4️⃣ Tenho clínica"
        ),
        "opcoes": {
            "1": "medico_estudante",
            "2": "medico_pf",
            "3": "medico_cnpj",
            "4": "medico_clinica"
        }
    },
    "especialista": {
        "mensagem": "Ok! Vou te direcionar para um especialista humano agora 👨‍💼",
        "opcoes": {}
    },
    # Adicione os demais nós conforme seu fluxo completo...
}

# Credenciais do Z-API (configure no Render)
INSTANCE = os.environ.get("ZAPI_INSTANCE")
TOKEN = os.environ.get("ZAPI_TOKEN")
BASE_URL = f"https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}"

# Validação das credenciais na inicialização
if not INSTANCE or not TOKEN:
    print("🚨 ERRO: As variáveis de ambiente ZAPI_INSTANCE e ZAPI_TOKEN não foram configuradas.")
    print("🚨 O aplicativo não pode iniciar sem as credenciais.")
    exit() # Impede a execução do app se as credenciais estiverem ausentes

# Função para enviar mensagem via Z-API
def enviar_msg(numero, texto):
    url = f"{BASE_URL}/send-message"
    payload = {
        "phone": numero,
        "message": texto
    }

    print("📤 Tentando enviar mensagem via Z-API...")
    print("➡️ URL:", url)
    print("➡️ Payload:", payload)

    try:
        resp = requests.post(url, json=payload, timeout=10)
        print("🔁 Resposta da Z-API (Status):", resp.status_code)
        print("🔁 Resposta da Z-API (Corpo):", resp.text)

        if resp.status_code == 200:
            try:
                response_json = resp.json()
                if response_json.get("error"):
                    print(f"🚨 Erro reportado pela Z-API: {response_json.get('error')} - {response_json.get('message')}")
                    return False # Indica falha no envio
                elif response_json.get("id"): # Z-API geralmente retorna um ID para mensagens bem-sucedidas
                    print("✅ Mensagem enviada com sucesso!")
                    return True # Indica sucesso no envio
                else:
                    print("⚠️ Resposta da Z-API 200 OK, mas formato inesperado:", response_json)
                    return False
            except requests.exceptions.JSONDecodeError:
                print("⚠️ Resposta da Z-API 200 OK, mas não é JSON válido.")
                return False
        else:
            resp.raise_for_status() # Isso levantará uma exceção para 4xx/5xx
            return True # Se raise_for_status não levantou, é um status 2xx diferente de 200
    except requests.exceptions.HTTPError as http_err:
        print(f"🚨 Erro HTTP ao enviar mensagem: {http_err}")
        print(f"🚨 Resposta do servidor (se disponível): {http_err.response.text if http_err.response else 'N/A'}")
        return False
    except requests.exceptions.ConnectionError as conn_err:
        print(f"🚨 Erro de conexão ao enviar mensagem: {conn_err}")
        return False
    except requests.exceptions.Timeout as timeout_err:
        print(f"🚨 Tempo limite excedido ao enviar mensagem: {timeout_err}")
        return False
    except Exception as e:
        print(f"🚨 Erro geral ao enviar mensagem: {e}")
        return False

# Rota principal para evitar erro 404
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot ativo e rodando!", 200

# Rota de verificação de saúde
@app.route("/health", methods=["GET"])
def health():
    return "healthy", 200

# Webhook que recebe mensagens do Z-API
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data:
            print("⚠️ Webhook recebido, mas sem payload JSON.")
            return "ignorado", 200
            
        print("📩 Payload recebido:", data)

        # Z-API pode enviar diferentes tipos de eventos. Ignoramos os que não são mensagens.
        if data.get("isGroup") or not data.get("text"):
            print("🚫 Ignorando mensagem de grupo ou evento sem texto.")
            return "ignorado", 200

        numero = data.get("phone")
        texto = data.get("text", {}).get("message") # A mensagem vem dentro de "text"

        print(f"📞 Número: {numero} | ✉️ Texto: {texto}")

        if not numero or not texto:
            print("⚠️ Número ou texto ausente no payload.")
            return "ignorado", 200

        # Lógica do fluxo do chatbot
        estado = user_states.get(numero, "inicio")
        no = fluxo.get(estado, fluxo["inicio"])
        print(f"🔄 Estado atual: {estado}")

        opcoes_validas = no.get("opcoes", {})
        if texto.strip() in opcoes_validas:
            prox = opcoes_validas[texto.strip()]
            user_states[numero] = prox
            print(f"➡️ Próximo estado: {prox}")
            enviar_msg(numero, fluxo[prox]["mensagem"])
        else:
            # Se a opção for inválida ou o estado foi perdido, reinicia a conversa.
            print("❌ Opção inválida ou estado perdido. Reiniciando fluxo.")
            user_states[numero] = "inicio" # Reseta o estado
            mensagem_inicial = fluxo["inicio"]["mensagem"]
            enviar_msg(numero, "Opção inválida. Vamos tentar de novo do começo, ok?\n\n" + mensagem_inicial)

    except Exception as e:
        print(f"🚨 Erro crítico no processamento do webhook: {e}")

    return "ok", 200

# Inicialização do servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
