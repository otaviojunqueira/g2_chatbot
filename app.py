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

# Função para enviar mensagem via Z-API
def enviar_msg(numero, texto):
    url = f"{BASE_URL}/send-message"
    payload = {"phone": numero, "message": texto}
    print("📤 Enviando mensagem:", payload)
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("✅ Mensagem enviada com sucesso:", resp.json())
    except Exception as e:
        print("🚨 Erro ao enviar mensagem:", e)

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
    data = request.get_json(force=True)
    print("📩 Payload recebido:", data)

    try:
        numero = data.get("phone")
        texto = data.get("message")

        print(f"📞 Número: {numero} | ✉️ Texto: {texto}")

        if not numero or not texto:
            print("⚠️ Número ou texto ausente")
            return "ignorado", 200

        estado = user_states.get(numero, "inicio")
        no = fluxo.get(estado, fluxo["inicio"])
        print(f"🔄 Estado atual: {estado}")

        if texto in no.get("opcoes", {}):
            prox = no["opcoes"][texto]
            user_states[numero] = prox
            print(f"➡️ Próximo estado: {prox}")
            enviar_msg(numero, fluxo[prox]["mensagem"])
        else:
            print("❌ Opção inválida, reenviando menu atual")
            enviar_msg(numero, "Opção inválida. Tente novamente:\n\n" + no["mensagem"])

    except Exception as e:
        print("🚨 Erro no webhook:", e)

    return "ok", 200

# Inicialização do servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
