# def test_llm_parse_document_with_yield(monkeypatch):
#     def fake_create(*args, **kwargs):
#         class Resp:
#             choices = [
#                 type(
#                     "Obj",
#                     (),
#                     {
#                         "message": type(
#                             "M",
#                             (),
#                             {
#                                 "content": '{"summary":"test","reagents":[],"solvents":[],"conditions":{},"yield_percentage":85.0}'
#                             },
#                         )()
#                     },
#                 )()
#             ]

#         return Resp()

#     monkeypatch.setattr("openai.OpenAI.chat.completions.create", fake_create)

#     from app.services.parser import llm_parse_document

#     result = llm_parse_document("fake reaction")
#     assert result.summary == "test"
#     assert result.yield_percentage == 85.0
