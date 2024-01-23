from contextlib import ExitStack

from cherrypy import (
    tree, 
    engine, 
    server, 
    dispatch,
)

from ...controller import Controller
from ...config import Config

from .endpoints import (
    API,
    UI,
)


class Website():

    exit_stack: ExitStack
    config: Config
    controller: Controller

    def __init__(self, config: Config, /, dry_run: bool = False, controller: Controller | None = None):
        self.exit_stack = ExitStack()
        self.config = config
        self.controller = controller or Controller(config, dry_run=dry_run)

    def mount_api(self):
        endpoint = API(self.controller)
        dispatcher = dispatch.RoutesDispatcher()
        dispatcher.connect("api", "/pictures/{id}", controller=endpoint, action="get_picture", conditions=dict(method=["GET"]))
        dispatcher.connect("api", "/pictures/{id}/thumbnail", controller=endpoint, action="download_picture_thumbnail", conditions=dict(method=["GET"]))
        dispatcher.connect("api", "/pictures/{id}/content", controller=endpoint, action="download_picture_content", conditions=dict(method=["GET"]))
        dispatcher.connect("api", "/pictures", controller=endpoint, action="take_picture", conditions=dict(method=["POST"]))
        dispatcher.connect("api", "/pictures", controller=endpoint, action="list_pictures", conditions=dict(method=["GET"]))
        tree.mount(None, "/api", config={
            "/": {
                "request.dispatch": dispatcher,
            },
        })

    def mount_ui(self):
        ui_folder_path = self.config.values.website.ui_folder_path
        endpoint = UI(ui_folder_path)
        dispatcher = dispatch.RoutesDispatcher()
        dispatcher.connect("ui", "/assets/{url_path:.*}", controller=endpoint, action="serve_assets", conditions=dict(method=["GET"]))
        dispatcher.connect("ui", "/{url_path:.*}", controller=endpoint, action="serve_index", conditions=dict(method=["GET"]))
        tree.mount(None, "/", config={
            "/": {
                "request.dispatch": dispatcher,
            },
        })

    def __enter__(self):
        self.exit_stack.enter_context(self.controller)

        self.mount_api()
        self.mount_ui()
        
        server.socket_host = str(self.config.values.website.host)
        server.socket_port = self.config.values.website.port
        engine.start()
        return self
    

    def __exit__(self, type, value, trackeback):
        engine.exit()
        self.exit_stack.close()

    def serve_forever(self):
        engine.block()
