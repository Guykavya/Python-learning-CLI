code = int(input())
match code:
    case 200:
        text = "OK"
    case 201:
        text = "Created"
    case 204:
        text = "No Content"
    case 301 | 302 | 307 | 308:
        text = "Redirect"
    case 401 | 403:
        text = "Not Allowed"
    case 404:
        text = "Not Found"
    case n if 400 <= n <= 499:
        text = "Client Error"
    case n if 500 <= n <= 599:
        text = "Server Error"
    case _:
        text = "Unknown"
print(f"{code} {text}")
