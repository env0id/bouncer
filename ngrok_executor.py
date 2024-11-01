import os

from pyngrok import ngrok
import os

def start_ngrok():
  ngrok_token = os.environ.get("NGROK_TOKEN")
  port = os.environ.get("WEBAPP_PORT")
  domain = os.environ.get("DOMAIN")
  ngrok.set_auth_token(ngrok_token)
  http_tunnel = ngrok.connect(addr=f"{port}", bind_tls=True, domain=domain)
  return http_tunnel.public_url