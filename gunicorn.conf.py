from gateways import ssh_tunnel


def on_starting(server):
    server.ssh_processes = ssh_tunnel.open_tunnels()


def on_reload(server):
    ssh_tunnel.close_tunnels(server.ssh_processes)
    server.ssh_processes = ssh_tunnel.open_tunnels()


def worker_exit(server, worker):
    ssh_tunnel.close_tunnels(server.ssh_processes)
