# dns
Domain Name System (DNS) server and client implementation in Python. Supports building and parsing DNS messages.

```

                Local Host                        |  Foreign
                                                |
+---------+               +----------+         |  +--------+
|         | user queries  |          |queries  |  |        |
|  User   |-------------->|          |---------|->|Foreign |
| Program |               | Resolver |         |  |  Name  |
|         |<--------------|          |<--------|--| Server |
|         | user responses|          |responses|  |        |
+---------+               +----------+         |  +--------+
                            |     A            |
            cache additions |     | references |
                            V     |            |
                            +----------+         |
                            |  cache   |         |
                            +----------+         |

```

## Running
- Server
```bash
python3 server.py --resolver 8.8.8.8:53
```

- Client
```bash
python3 client.py <domain>
```

## To-Do
- [ ] Add parsing for authority and additional records
- [ ] Resolve recursively to find records