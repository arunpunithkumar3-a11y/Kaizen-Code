from langchain_openai import ChatOpenAI

from kaizen.storage.config.config_manager import config_service


def get_llm():
    conifg_data = config_service.show_config()
    data = conifg_data.get("config", "")
    llm = ChatOpenAI(
        base_url=data["KAIZEN_BASE_URL"],
        model=data["KAIZEN_MODEL"],
        api_key=data["KAIZEN_API_KEY"],
    )
    return llm
