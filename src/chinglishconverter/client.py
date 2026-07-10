"""Thin wrapper around the Anthropic Claude client used by the converter."""

from __future__ import annotations

from typing import Optional

from chinglishconverter import config

DEFAULT_MODEL = "claude-opus-4-8"
# Streaming is used, so a large ceiling is safe; the model stops when done.
DEFAULT_MAX_TOKENS = 32000


class AuthError(RuntimeError):
    """Raised when no Anthropic credentials can be found."""


class ConversionAPIError(RuntimeError):
    """Raised when the Claude API call fails."""


class ChinglishClient:
    """Wraps ``anthropic.Anthropic`` and exposes a single ``rewrite`` call."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        try:
            import anthropic  # imported lazily so --help works without the dep
        except ImportError as exc:  # pragma: no cover
            raise AuthError(
                "The 'anthropic' package is not installed. Run: pip install anthropic"
            ) from exc

        self._anthropic = anthropic
        self.model = model

        key = api_key or config.resolve_api_key()
        try:
            # If key is None the SDK still resolves ANTHROPIC_AUTH_TOKEN or an
            # `ant auth login` profile, so we let it try rather than hard-fail.
            self._client = anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()
        except Exception as exc:  # pragma: no cover - defensive
            raise AuthError(str(exc)) from exc

    def rewrite(self, system_prompt: str, text: str, *,
                max_tokens: int = DEFAULT_MAX_TOKENS,
                effort: str = "medium") -> str:
        """Send one chunk of text through the model and return the rewrite.

        Uses streaming (recommended for potentially long output) with adaptive
        thinking so the model can reason about tricky calques.
        """
        anthropic = self._anthropic
        try:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                thinking={"type": "adaptive"},
                output_config={"effort": effort},
                messages=[{"role": "user", "content": text}],
            ) as stream:
                message = stream.get_final_message()
        except anthropic.AuthenticationError as exc:
            raise AuthError(
                "Authentication failed. Check your API key (run: chinglish login)."
            ) from exc
        except anthropic.APIStatusError as exc:
            raise ConversionAPIError(f"API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise ConversionAPIError(
                "Could not reach the Anthropic API. Check your network connection."
            ) from exc

        if message.stop_reason == "refusal":
            raise ConversionAPIError(
                "The model declined to process this content."
            )

        parts = [block.text for block in message.content if block.type == "text"]
        return "".join(parts).strip("\n")
