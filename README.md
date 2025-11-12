
---

# Chatbot de Atendimento para Área da Saúde (WhatsApp + Python)

## 📌 Visão Geral
Este projeto implementa um **chatbot de atendimento automatizado para WhatsApp**, desenvolvido em **Python** com **Flask**.  
O bot foi desenhado para atender profissionais da área da saúde (médicos, dentistas, fisioterapeutas e psicólogos), oferecendo uma jornada de atendimento clara, acolhedora e eficiente.

O objetivo é **qualificar leads**, **diagnosticar dores específicas** e **direcionar para soluções adequadas**, aumentando a eficiência do atendimento e as chances de conversão.

---

## Objetivos do Chatbot
- Atendimento **24/7** com linguagem conversacional.  
- Jornada personalizada conforme o perfil do profissional.  
- Diagnóstico de necessidades (ex: impostos altos, troca de contador, abertura de CNPJ).  
- Captura de leads qualificados com chamadas claras para ação (orçamento, análise, falar com especialista).  
- Redução de custos operacionais e aumento da escalabilidade do atendimento.  

---

## Tecnologias Utilizadas
- **Python 3.10+**  
- **Flask** → servidor web para receber e responder mensagens.  
- **Requests** → integração com a API do WhatsApp Business (ou Twilio/Zenvia).  
- **Estrutura em dicionário/JSON** → representação da árvore de decisão do fluxo de atendimento.  
- **Hospedagem**: Railway, Render, Heroku, AWS, Azure ou GCP.  

---

## 📂 Estrutura do Fluxo
O fluxo foi desenhado para contemplar **4 perfis principais**:

1.   **Médicos**  
   - Estudante/recém-formado  
   - Atendendo como PF  
   - Já com CNPJ  
   - Dono de clínica  

2.   **Dentistas**  
   - Recém-formado ou atuando em clínicas  
   - Já com CNPJ  
   - Dono de clínica odontológica  

3.   **Fisioterapeutas**  
   - Atendendo como PF  
   - Já com CNPJ  
   - Dono de estúdio/clínica  

4.   **Psicólogos**  
   - Recém-formado ou PF  
   - Já com CNPJ  
   - Dono de consultório ou espaço terapêutico  

Cada fluxo termina em uma **chamada para ação clara**: pedir orçamento, solicitar análise tributária ou falar com um especialista humano.

---

##  Como Funciona
1. O usuário envia uma mensagem para o número do WhatsApp Business.  
2. O servidor Flask recebe a mensagem via **webhook**.  
3. O bot identifica em qual ponto do fluxo o usuário está e responde com a próxima mensagem.  
4. As escolhas do usuário são armazenadas em memória (ou banco de dados, em produção).  
5. O fluxo segue até a captura do lead ou encaminhamento para atendimento humano.  

---

##  Instalação e Execução

### 1. Clonar o repositório
```bash
git clone https://github.com/otaviojunqueira/g2_chatbot
cd g2_chatbot
```

### 2. Criar ambiente virtual e instalar dependências
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Crie um arquivo `.env` com:
```
TOKEN=seu_token_do_whatsapp
PHONE_ID=seu_phone_id
```

### 4. Rodar o servidor
```bash
python app.py
```

### 5. Expor localmente (para testes)
Use o **ngrok**:
```bash
ngrok http 5000
```
Configure a URL gerada no **Webhook do WhatsApp Business**.

---

##  Hospedagem
O projeto pode ser hospedado em:
- **Railway / Render** → fácil deploy, ideal para MVPs.  
- **AWS / Azure / GCP** → robustez e escalabilidade para produção.  
- **Heroku** → alternativa simples (planos pagos).  

---

## Benefícios para o Cliente
- Atendimento rápido e humanizado.  
- Redução de custos com suporte.  
- Relatórios de uso e otimização contínua.  
- Escalabilidade: fácil adicionar novos fluxos e integrações.  

---

## Próximos Passos
- Integração com CRM para salvar leads automaticamente.  
- Dashboards de relatórios em tempo real.  
- Uso de IA para respostas abertas além do fluxo pré-definido.  

---
