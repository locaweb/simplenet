===
API
===

Nota::

  Aqui pode ser adicionado alguma informaçào sobre a API

/v1/endpoint
============

Método GET
----------

:status: * 200 Ok
         * xxx Erro

Retorna todos os recursos sobre esse endpoint

Exemplos::

  $ curl <endpoint>/v1/endpoint.json -H "Current-User: locaweb"
  [{"id": 123, "name": "Locawe"}]


Método POST
-----------

:status: * 200 Ok
         * xxx Erro

Cria um novo recurso nesse endpoint.

**OBS**: Exemplo de observações e notas sobre a API

Exemplos::

  $ curl <endpoint>/v1/endpoint.json -H "Current-User: locaweb" -X POST -d "endpoint[name]=locaweb"
  {"id": 123, "name": "locaweb"}
