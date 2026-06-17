from app.core.config import get_settings

settings = get_settings()

print(settings.qwen_base_url)
print(settings.qwen_model_name)