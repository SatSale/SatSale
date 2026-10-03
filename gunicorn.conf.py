from gateways import ssh_tunnel


def on_starting(server):
    server.ssh_processes = ssh_tunnel.open_tunnels()


def on_reload(server):
    ssh_tunnel.close_tunnels(server.ssh_processes)
    server.ssh_processes = ssh_tunnel.open_tunnels()


def pre_fork(server, worker):
    if server.ssh_processes is None:
        server.ssh_processes = ssh_tunnel.open_tunnels()

def worker_exit(server, worker):
    if server.ssh_processes is not None:
        ssh_tunnel.close_tunnels(server.ssh_processes)
