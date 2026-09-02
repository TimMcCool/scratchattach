import scratchattach as sa

from rich.traceback import install

from scratchattach.cloud.cloud import CustomCloud

install(show_locals=True)

server_ip = '127.0.0.1'
ws_server_port = 8080
wss_server_port = 8765
project_id=["108566337"]

ws_server = sa.init_cloud_server(server_ip,
                              ws_server_port,
                              length_limit=65536,
                              allow_non_numeric=True,
                              whitelisted_projects=project_id,
                              allow_nonscratch_names=True,
                              blocked_ips=None,
                              sync_players=True,
                              log_var_sets=True
)

wss_server = sa.init_ssl_cloud_server(server_ip,
                              wss_server_port,
                              length_limit=65536,
                              allow_non_numeric=True,
                              whitelisted_projects=project_id,
                              allow_nonscratch_names=True,
                              blocked_ips=None,
                              sync_players=True,
                              log_var_sets=True,
                              certfile="certfile.pem",
                              keyfile="keyfile.pem"
)



ws_server.start()

wss_server.start()

cloud = CustomCloud(project_id=project_id[0],
                    cloud_host=f"wss://{server_ip}:{wss_server_port}",
                    username = "Boss_1s",
                    length_limit = None,
                    allow_non_numeric = True,
                    _session = None,
                    header = None,
                    cookie = None,
                    origin = None,
                    print_connect_messages = True)

events = cloud.events()

events.start()
