from flask import Flask, request
import requests
import os

app = Flask(__name__)

# "Memória" simples para armazenar o estado de cada usuário (em produção use Redis/DB)
user_states = {}

# Estrutura do fluxo de atendimento (completo, baseado no documento)
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
        "opcoes": {"3": "trocar_contador"}
    },
    "medico_clinica": {
        "mensagem": (
            "Opções para clínicas:\n"
            "1️⃣ Otimizar impostos (Simples vs Presumido)\n"
            "2️⃣ Gestão financeira (Folha, BPO)\n"
            "3️⃣ Trocar de contador\n"
            "4️⃣ Dúvidas sobre contratação de equipe"
        ),
        "opcoes": {"3": "trocar_contador"}
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
        "opcoes": {"3": "trocar_contador"}
    },
    "dentista_clinica": {
        "mensagem": (
            "Opções para clínicas odontológicas:\n"
            "1️⃣ Como declarar venda de materiais\n"
            "2️⃣ Registro de equipamentos e TPD\n"
            "3️⃣ Gestão financeira completa\n"
            "4️⃣ Quero trocar de contador"
        ),
        "opcoes": {"4": "trocar_contador"}
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
        "opcoes": {"3": "trocar_contador"}
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
        "opcoes": {"3": "trocar_contador"}
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
    }
}

# Credenciais do Z-API (configure como variáveis de ambiente no Render)
INSTANCE = os.environ.get("ZAPI_INSTANCE")
TOKEN = os.environ.get("ZAPI_TOKEN")
BASE_URL = f"https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}"

# Função para enviar mensagem via Z-API
def enviar_msg(numero, texto):
    url = f"{BASE_URL}/send-message"
    payload = {"phone": numero, "message": texto}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("Mensagem enviada:", resp.json())
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# Webhook para receber mensagens do Z-API
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    try:
        # Ajuste conforme o payload real do Z-API (exemplo básico abaixo)
        numero = data.get("phone")
        texto = data.get("message")

        if not numero or not texto:
            return "ignorado", 200

        estado = user_states.get(numero, "inicio")
        no = fluxo.get(estado, fluxo["inicio"])

        if texto in no.get("opcoes", {}):
            prox = no["opcoes"][texto]
            user_states[numero] = prox
            enviar_msg(numero, fluxo[prox]["mensagem"])
        else:
            enviar_msg(numero, "Opção inválida. Tente novamente:\n\n" + no["mensagem"])

    except Exception as e:
        print("Erro no webhook:", e)

    return "ok", 200

@app.route("/health")
def health():
    return "healthy", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
