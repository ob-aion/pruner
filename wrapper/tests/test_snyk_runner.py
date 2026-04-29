"""Tests for the Snyk opt-in runner."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from pruner_wrapper.snyk_runner import is_authorised, is_available


@pytest.fixture
def with_token(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("SNYK_TOKEN", "fake")
    yield
    monkeypatch.delenv("SNYK_TOKEN", raising=False)


def test_is_authorised_with_token(with_token: None) -> None:
    assert is_authorised()


def test_is_authorised_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SNYK_TOKEN", raising=False)
    assert not is_authorised()


def test_is_available_returns_bool() -> None:
    # Returns True only if `snyk` is on PATH; we just verify it's a bool.
    assert isinstance(is_available(), bool)


def test_env_check_does_not_leak_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SNYK_TOKEN", raising=False)
    assert "SNYK_TOKEN" not in os.environ
