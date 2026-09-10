from glmv_reward.utils.misc import ensure_list, ensure_text


def test_ensure_list_wraps_single_string():
    # A str is a Sequence, but the public APIs (get_reward, verifier llm_api_key /
    # llm_judge_url / llm_model) accept a single string and must treat it as one
    # element instead of splitting it into characters.
    assert ensure_list("hello") == ["hello"]
    assert ensure_list("") == [""]
    assert ensure_list("https://open.bigmodel.cn/api/paas/v4/chat/completions") == [
        "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    ]


def test_ensure_list_wraps_single_bytes():
    assert ensure_list(b"hello") == [b"hello"]
    assert ensure_list(bytearray(b"hi")) == [bytearray(b"hi")]


def test_ensure_list_keeps_real_sequences():
    assert ensure_list(["a", "b"]) == ["a", "b"]
    assert ensure_list(("a", "b")) == ["a", "b"]
    assert ensure_list([]) == []


def test_ensure_list_wraps_non_sequence_scalars():
    assert ensure_list(5) == [5]
    assert ensure_list(1.5) == [1.5]
    assert ensure_list(None) == [None]


def test_ensure_text_passthrough_and_decode():
    assert ensure_text("abc") == "abc"
    assert ensure_text(b"abc") == "abc"
