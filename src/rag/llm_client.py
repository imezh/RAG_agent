"""LLM client implementations for YandexGPT and GigaChat."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        pass


class YandexGPTClient(LLMClient):
    """Client for YandexGPT API."""

    def __init__(
        self,
        api_key: str,
        folder_id: str,
        model: str = "yandexgpt-lite",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ):
        """
        Initialize YandexGPT client.

        Args:
            api_key: YandexCloud API key
            folder_id: YandexCloud folder ID
            model: Model name (yandexgpt-lite or yandexgpt)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        logger.info(f"Initialized YandexGPT client with model: {model}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using YandexGPT.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "text": system_prompt})
        messages.append({"role": "user", "text": prompt})

        data = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}/latest",
            "completionOptions": {
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            },
            "messages": messages,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            return result["result"]["alternatives"][0]["message"]["text"]

        except requests.exceptions.RequestException as e:
            logger.error(f"YandexGPT API error: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing YandexGPT response: {e}")
            raise


class GigaChatClient(LLMClient):
    """Client for GigaChat API."""

    def __init__(
        self,
        api_key: str,
        model: str = "GigaChat",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ):
        """
        Initialize GigaChat client.

        Args:
            api_key: GigaChat API key
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        self.access_token = self._get_access_token()
        logger.info(f"Initialized GigaChat client with model: {model}")

    def _get_access_token(self) -> str:
        """
        Get access token for GigaChat API.

        Returns:
            Access token
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"scope": "GIGACHAT_API_PERS"}

        try:
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=data,
                verify=False,  # GigaChat uses self-signed certificates
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["access_token"]

        except requests.exceptions.RequestException as e:
            logger.error(f"GigaChat auth error: {e}")
            raise

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using GigaChat.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                verify=False,  # GigaChat uses self-signed certificates
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"GigaChat API error: {e}")
            # Try to refresh token on auth error
            if response.status_code == 401:
                self.access_token = self._get_access_token()
                return self.generate(prompt, system_prompt)
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing GigaChat response: {e}")
            raise
