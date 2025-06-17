import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
)
from botbuilder.schema import Activity, ActivityTypes
from chat import process_message, send_menu

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

memory = MemoryStorage()
conversation_state = ConversationState(memory)
USER_PROFILE = "user_profile"

async def messages(req: web.Request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    async def aux_func(turn_context):
        if activity.type == ActivityTypes.message:
            await process_message(turn_context, conversation_state, USER_PROFILE)
        elif activity.type == ActivityTypes.conversation_update:
            if activity.members_added:
                for member in activity.members_added:
                    if member.id != activity.recipient.id:
                        await send_menu(turn_context, show_welcome=True)

    await adapter.process_activity(activity, auth_header, aux_func)
    return web.Response(status=201)

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    print("Bot rodando em http://localhost:3978/api/messages")
    web.run_app(app, host="localhost", port=3978)