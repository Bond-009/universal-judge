Aan de functie `${function("splits_in_woorden")}` moet een string (`${datatype("text")}`) doorgegeven worden.
De functie geeft een lijst van letters (`${datatype("sequence", "char")}`) terug.

```tested
a_function_call("yes")
```

% if programming_language == "python":
This is python.
% elif programming_language == "kotlin":
This is kotlin.
% elif programming_language == "java":
This is java.
% elif programming_language == "haskell":
This is haskell.
% endif

```console?lang=tested
>>> a_function_call("yes")
```
