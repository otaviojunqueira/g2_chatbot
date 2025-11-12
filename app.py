from flask import Flask, request
import requests
import os

app = Flask(__name__)

# "Memória" simples para armazenar o estado de cada usuário
user_states = {}

# Estrutura completa do fluxo de atendimento
fluxo = {
    "inicio": {
        "mensagem": (
            "Olá! 👋 Seja bem-vindo(a) à g2 soluções contábeis, "
            "sua parceira especializada em contabilidade para a área da saúde!\n\n"
            "Com qual profissional estou falando?\n"
            "1️⃣ Sou Médico(a)\n"
            "2️⃣ Sou Dentista\n"
            "3️⃣ Sou Fisioterapeuta\n"
            "4️⃣ Sou Psicólogo(a)\n"
            "0️⃣ Falar com um especialista agora"
        ),
        "opcoes": {
            "1": "medico",
            "2": "dentista",
            "3": "fisioterapeuta",
            "4": "psicologo",
            "0": "especialista"
        }
    },

    # ---------------- MÉDICOS ----------------
    "medico": {
        "mensagem": (
            "Entendido! Como posso te ajudar hoje?\n"
            "1️⃣ Sou estudante ou recém-formado\n"
            "2️⃣ Faço plantões ou atendo como PF\n"
            "3️⃣ Já tenho CNPJ\n"
            "4️⃣ Tenho (ou quero montar) clínica"
        ),
        "opcoes": {
            "1": "medico_estudante",
            "2": "medico_pf",
            "3": "medico_cnpj",
            "4": "medico_clinica"
        }
    },
    "medico_estudante": {
        "mensagem": (
            "Opções para estudantes:\n"
            "1️⃣ Dúvidas sobre abrir CNPJ\n"
            "2️⃣ Diferença PF vs PJ\n"
            "3️⃣ Orçamento para abertura de empresa"
        ),
        "opcoes": {}
    },
    "medico_pf": {
        "mensagem": (
            "Opções para quem atua como PF:\n"
            "1️⃣ Simulação: Imposto PF vs CNPJ\n"
            "2️⃣ Como abrir CNPJ para reduzir impostos\n"
            "3️⃣ Já tenho CNPJ mas não sei se pago corretamente"
        ),
        "opcoes": {}
    },
    "medico_cnpj": {
        "mensagem": (
            "Já tem CNPJ? Veja opções:\n"
            "1️⃣ Análise tributária gratuita\n"
            "2️⃣ Ajuda com finanças (Pró-labore, lucros)\n"
            "3️⃣ Quero trocar de contador"
        ),
        "opcoes": {
            "3": "trocar_contador"
        }
    },
    "medico_clinica": {
        "mensagem": (
            "Opções para clínicas:\n"
            "1️⃣ Otimizar impostos (Simples vs Presumido)\n"
            "2️⃣ Gestão financeira (Folha, BPO)\n"
            "3️⃣ Trocar de contador\n"
            "4️⃣ Dúvidas sobre contratação de equipe"
        ),
        "opcoes": {
            "3": "trocar_contador"
        }
    },

    # ---------------- DENTISTAS ----------------
    "dentista": {
        "mensagem": (
            "Ótimo! Para dentistas, temos soluções específicas:\n"
            "1️⃣ Sou recém-formado ou trabalho em clínicas\n"
            "2️⃣ Já tenho CNPJ\n"
            "3️⃣ Tenho clínica odontológica"
        ),
        "opcoes": {
            "1": "dentista_recem",
            "2": "dentista_cnpj",
            "3": "dentista_clinica"
        }
    },
    "dentista_recem": {
        "mensagem": (
            "Opções para recém-formados:\n"
            "1️⃣ Vale a pena abrir CNPJ?\n"
            "2️⃣ Como funciona o Carnê-Leão?\n"
            "3️⃣ Orçamento para abrir CNPJ"
        ),
        "opcoes": {}
    },
    "dentista_cnpj": {
        "mensagem": (
            "Já tem CNPJ? Veja opções:\n"
            "1️⃣ O que é o Fator R?\n"
            "2️⃣ Revisão tributária (Simples vs Presumido)\n"
            "3️⃣ Quero trocar de contador"
        ),
        "opcoes": {
            "3": "trocar_contador"
        }
    },
    "dentista_clinica": {
        "mensagem": (
            "Opções para clínicas odontológicas:\n"
            "1️⃣ Como declarar venda de materiais\n"
            "2️⃣ Registro de equipamentos e TPD\n"
            "3️⃣ Gestão financeira completa\n"
            "4️⃣ Quero trocar de contador"
        ),
        "opcoes": {
            "4": "trocar_contador"
        }
    },

    # ---------------- FISIOTERAPEUTAS ----------------
    "fisioterapeuta": {
        "mensagem": (
            "Perfeito! A contabilidade para fisioterapeutas tem suas particularidades:\n"
            "1️⃣ Atendo como PF\n"
            "2️⃣ Já tenho CNPJ\n"
            "3️⃣ Tenho estúdio/clínica"
        ),
        "opcoes": {
            "1": "fisio_pf",
            "2": "fisio_cnpj",
            "3": "fisio_clinica"
        }
    },
    "fisio_pf": {
        "mensagem": (
            "Opções para PF:\n"
            "1️⃣ Simulação: economia com CNPJ\n"
            "2️⃣ Como declarar recebimentos de planos\n"
            "3️⃣ Orçamento para abrir CNPJ"
        ),
        "opcoes": {}
    },
    "fisio_cnpj": {
        "mensagem": (
            "Já tem CNPJ? Veja opções:\n"
            "1️⃣ O Fator R se aplica?\n"
            "2️⃣ Revisão tributária\n"
            "3️⃣ Quero trocar de contador"
        ),
        "opcoes": {
            "3": "trocar_contador"
        }
    },
    "fisio_clinica": {
        "mensagem": (
            "Opções para clínicas de fisioterapia:\n"
            "1️⃣ Impostos ao alugar salas\n"
            "2️⃣ Melhor forma de contratar equipe\n"
            "3️⃣ Assessoria em gestão financeira"
        ),
        "opcoes": {}
    },

    # ---------------- PSICÓLOGOS ----------------
    "psicologo": {
        "mensagem": (
            "Entendido! A contabilidade para psicólogos é uma de nossas especialidades:\n"
            "1️⃣ Sou recém-formado ou atendo como PF\n"
            "2️⃣ Já tenho CNPJ\n"
            "3️⃣ Tenho consultório ou espaço terapêutico"
        ),
        "opcoes": {
            "1": "psico_pf",
            "2": "psico_cnpj",
            "3": "psico_clinica"
        }
    },
    "psico_pf": {
        "mensagem": (
            "Opções para PF:\n"
            "1️⃣ Preciso abrir CNPJ para atender\n"
            "2️⃣ Simulação: PF vs PJ\n"
            "3️⃣ Como declarar no Carnê-Leão"
        ),
        "opcoes": {}
    },
    "psico_cnpj": {
        "mensagem": (
            "Já tem CNPJ? Veja opções:\n"
            "1️⃣ Psicólogo pode ser MEI?\n"
            "2️⃣ Como o Fator R pode ajudar\n"
            "3️⃣ Quero trocar de contador"
        ),
        "opcoes": {
            "3": "trocar_contador"
        }
    },
    "psico_clinica": {
        "mensagem": (
            "Opções para consultórios:\n"
            "1️⃣ Como declarar custos de aluguel\n"
            "2️⃣ Melhor modelo de sociedade\n"
            "3️⃣ Organização financeira do consultório"
        ),
        "opcoes": {}
    },

    # ---------------- FLUXO COMUM ----------------
    "trocar_contador": {
        "mensagem": (
            "Entendi que você deseja trocar de contador. Pode me dizer o motivo?\n"
            "1️⃣ Meu contador não é especialista na área\n"
            "2️⃣ Sinto que pago muito imposto\n"
            "3️⃣ Atendimento e comunicação ruins"
        ),
        "opcoes": {}
    },
    "especialista": {
        "mensagem": "Ok! Vou te direcionar para um especialista humano agora 👨‍💼",
        "opcoes": {}
    },
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
    url = f"{BASE_URL}/send-text"
    payload = {
        "phone": numero,
        "message": texto
    }

    print("📤 Tentando enviar mensagem via Z-API...")
    print("➡️ URL:", url)
    print("➡️ Payload:", payload)

    response = None  # Inicializa a variável de resposta
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        print("🔁 Resposta da Z-API (Status):", response.status_code)
        print("🔁 Resposta da Z-API (Corpo):", response.text)

        # Verificação adicional para erros reportados no corpo da resposta da Z-API
        response_json = response.json()
        if response_json.get("error"):
            print(f"🚨 Erro reportado pela Z-API: {response_json.get('message')}")
            return False

        print("✅ Mensagem enviada com sucesso!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"🚨 Erro ao enviar mensagem via Z-API: {e}")
        if response is not None:
            print("🚨 Detalhes da resposta:", response.status_code, response.text)
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
