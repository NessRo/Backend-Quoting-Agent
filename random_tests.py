response = {"success":False, "comments": "hello"}


response.setdefault('comments', 'llm failed to structure data')

print(response)