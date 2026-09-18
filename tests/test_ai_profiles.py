from fastapi_backbone.ai.profiles import (
    GEMINI_PROFILE,
    OLLAMA_PROFILE,
    OPENAI_COMPATIBLE_PROFILE,
    OPENAI_PROFILE,
    get_provider_profile,
)


def test_concrete_provider_profiles_cover_supported_configuration() -> None:
    assert OPENAI_PROFILE.api_key_environment == "OPENAI_API_KEY"
    assert GEMINI_PROFILE.api_key_environment == "GEMINI_API_KEY"
    assert OLLAMA_PROFILE.default_base_url == "http://localhost:11434"
    assert (
        OPENAI_COMPATIBLE_PROFILE.base_url_environment
        == "OPENAI_COMPATIBLE_BASE_URL"
    )


def test_provider_profile_lookup_is_normalized() -> None:
    assert get_provider_profile(" OpenAI ").name == "openai"
    assert get_provider_profile("OLLAMA").name == "ollama"


def test_unknown_provider_profile_fails_closed() -> None:
    try:
        get_provider_profile("unknown")
    except ValueError as exc:
        assert "unknown AI provider profile" in str(exc)
    else:
        raise AssertionError("unknown provider profile should fail")
