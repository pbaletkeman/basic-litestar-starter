from typing import Annotated, Optional

import anyio
import litestar
from litestar import Litestar, post, Controller, get
from litestar.connection import request
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.mako import MakoTemplateEngine
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.openapi import OpenAPIConfig, OpenAPIController
from litestar.params import Body, Parameter
from litestar.response import Template
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig


class MyAPIController(Controller):
    path = 'api/v1'

    @post(path="/upload-file", tags=['My Tag'])
    async def handle_file_upload(self,
                                 data: Annotated[list[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
                                 ) -> list[str]:
        """
        ### Sample file upload
        #### put markdown here

        param data: form data

        return:

        **list of uploaded files**
        """
        file_names: list[str] = []
        for file in data:
            content = await file.read()
            await anyio.Path(file.filename).write_bytes(content)
            file_names.append(file.filename)

        return file_names

    @get(path='/sample/{variable:str}')
    async def display_variable(self, variable: str) -> str:
        return variable

    @get(path='/querystring')
    async def display_querystring(self,
                                  variable: str = Parameter(title='Variable', description='## sample variable ##')
                                  ) -> str:
        return variable


class MyUIController(Controller):
    dependencies = {"htmx_request": Provide(HTMXRequest)}

    @get(path='htmx', sync_to_thread=False, tags=['HTMX'])
    async def htmx_sample(self, htmx_request: HTMXRequest) -> str:
        if htmx_request.htmx:
            return htmx_request.htmx.current_url
        else:
            return htmx_request.method

    @get(path='/', sync_to_thread=False, tags=['UI'])
    async def index(self, name: Optional[str]) -> Template:
        """
        :param name: name is a querystring parameter
        :return:
        """
        return Template(template_name='index.mako.html', context={"sampleObj": name})

    @get(path='/tailwind', sync_to_thread=False, tags=['UI'])
    async def tailwind_index(self, name: Optional[str]) -> Template:
        """
        :param name: name is a querystring parameter
        :return:
        """
        return Template(template_name='tailwind.index.mako.html', context={"sampleObj": name})


class OpenAPIControllerExtra(OpenAPIController):
    favicon_url = '/static-files/favicon.ico'


async def on_startup():
    """
    sample start up script
    """
    pass


app = Litestar(
    route_handlers=[MyAPIController, MyUIController],
    on_startup=[on_startup],
    openapi_config=OpenAPIConfig(
        title='My API', version='1.0.0',
        root_schema_site='elements',  # swagger, elements, redoc, rapidoc
        path='/docs',
        create_examples=False,
        openapi_controller=OpenAPIControllerExtra,
        use_handler_docstrings=True,
    ),
    static_files_config=[StaticFilesConfig(
        path='static-files',  # path used in links
        directories=['static-files']  # path on the server
    )],
    request_class=HTMXRequest,
    template_config=TemplateConfig(engine=MakoTemplateEngine, directory="templates"),
)


# uvicorn main:app