import aiohttp
import difflib
from botbuilder.schema import Activity, ActivityTypes, SuggestedActions, CardAction, ActionTypes

BOLETO_MSG = "Para emitir boletos, acesse o portal do aluno e clique em 'Financeiro'."
CALENDARIO_MSG = "O calendário acadêmico está disponível em: https://blog.ibmec.br/wp-content/uploads/2025/05/Calendario-Academico_2025_1_V3-Ibmec5_RJ.pdf"
SECRETARIA_MSG = "Entre em contato com a secretaria pelo numero: 0800 771 8020"
HORARIO_MSG = "As aulas acontecem de segunda a sexta, das 19h às 22h."

KEYWORDS = {
    "matrícula": ["matricula", "matrícula"],
    "boleto": ["boleto"],
    "calendário": ["calendario", "calendário"],
    "horário": ["horario", "horário"],
    "secretaria": ["secretaria"]
}

def get_intent(text):
    words = text.split()
    options = [k for k in KEYWORDS]
    # Procura por aproximação em cada palavra da frase
    for word in words:
        match = difflib.get_close_matches(word, options, n=1, cutoff=0.7)
        if match:
            return match[0]
        # Também procura nas variações de cada keyword
        for key, variations in KEYWORDS.items():
            if difflib.get_close_matches(word, variations, n=1, cutoff=0.7):
                return key
    return None

async def send_menu(turn_context, show_welcome=False):
    if show_welcome:
        await turn_context.send_activity("Olá! Bem-vindo ao Bot do IBMEC!")
        await turn_context.send_activity("Selecione uma das opções abaixo para obter mais informações:")

    reply = Activity(
        type=ActivityTypes.message,
        suggested_actions=SuggestedActions(
            actions=[
                CardAction(title="Matrícula", type=ActionTypes.im_back, value="matrícula"),
                CardAction(title="Boleto", type=ActionTypes.im_back, value="boleto"),
                CardAction(title="Calendário", type=ActionTypes.im_back, value="calendário"),
                CardAction(title="Horário", type=ActionTypes.im_back, value="horário"),
                CardAction(title="Secretaria", type=ActionTypes.im_back, value="secretaria"),
            ]
        )
    )
    await turn_context.send_activity(reply)

async def process_message(turn_context, conversation_state, USER_PROFILE):
    user_data = await conversation_state.create_property(USER_PROFILE).get(turn_context, {}) or {}
    text = turn_context.activity.text.strip().lower()

    # Área de matrícula
    if user_data.get("matricula_step"):
        if user_data.get("matricula_step") == "nome":
            user_data["nome"] = turn_context.activity.text.strip()
            user_data["matricula_step"] = "email"
            await turn_context.send_activity("Qual seu e-mail?")
        elif user_data.get("matricula_step") == "email":
            user_data["email"] = turn_context.activity.text.strip()
            user_data["matricula_step"] = "curso"
            await turn_context.send_activity("Qual curso deseja se matricular?")
        elif user_data.get("matricula_step") == "curso":
            user_data["curso"] = turn_context.activity.text.strip()
            await turn_context.send_activity("Registrando sua matrícula...")

            matricula_payload = {
                "nome": user_data["nome"],
                "email": user_data["email"],
                "curso": user_data["curso"]
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:8080/api/matriculas",
                        json=matricula_payload,
                        timeout=10
                    ) as resp:
                        if resp.status in [200, 201]:
                            await turn_context.send_activity("Matrícula realizada com sucesso!")
                        else:
                            await turn_context.send_activity("Erro ao registrar matrícula. Tente novamente.")
            except Exception:
                await turn_context.send_activity("Erro ao conectar com o sistema de matrícula.")

            user_data.clear()
            await send_menu(turn_context)
        await conversation_state.create_property(USER_PROFILE).set(turn_context, user_data)
        await conversation_state.save_changes(turn_context)
        return

    # Detecta intenção mesmo com erro de digitação
    intent = get_intent(text)

    if intent == "boleto":
        await turn_context.send_activity(BOLETO_MSG)
        await send_menu(turn_context)
        return

    if intent == "calendário":
        await turn_context.send_activity(CALENDARIO_MSG)
        await send_menu(turn_context)
        return

    if intent == "horário":
        await turn_context.send_activity(HORARIO_MSG)
        await send_menu(turn_context)
        return

    if intent == "secretaria":
        await turn_context.send_activity(SECRETARIA_MSG)
        await send_menu(turn_context)
        return

    if intent == "matrícula":
        user_data["matricula_step"] = "nome"
        await turn_context.send_activity("Vamos iniciar sua matrícula! Qual seu nome?")
        await conversation_state.create_property(USER_PROFILE).set(turn_context, user_data)
        await conversation_state.save_changes(turn_context)
        return

    # Mensagem padrão + menu
    await turn_context.send_activity("Desculpe, não entendi. Por favor, escolha uma das opções abaixo:")
    await send_menu(turn_context)