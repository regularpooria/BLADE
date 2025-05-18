from scripts.embedding import search_bug


def test_search_bug():
    query_bug = {
        "symptom": "Operations on NoneType",
        "stack_trace": "TypeError: 'NoneType' object is not subscriptable",
        "buggy_code": "a = lista[1] - lista[0]",
    }
    search_bug(query_bug)
